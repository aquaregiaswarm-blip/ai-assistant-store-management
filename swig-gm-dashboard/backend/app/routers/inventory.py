"""Inventory and COGS endpoints."""
from fastapi import APIRouter, Query
from typing import Optional
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/inventory", tags=["inventory"])

# Dataset prefix for BigQuery table references
DS = f"{settings.gcp_project_id}.{settings.bigquery_dataset}"


@router.get("/daily-usage")
async def get_daily_usage(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get ingredient usage calculated from sales."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query(f"""
        SELECT
            inv.Inventory_ID,
            inv.Description as ingredient_name,
            inv.Category,
            inv.Recipe_UOM as unit,
            inv.Unit_Cost,
            inv.Count_UOM,
            inv.Conversion_Factor,
            SUM(li.Quantity * rbm.Quantity_Required * (1 + rbm.Yield_Loss_Pct)) as total_quantity_used
        FROM `{DS}.Sales_Order_Line_Items` li
        JOIN `{DS}.Sales_Transactions_Header` t ON li.Transaction_UUID = t.Transaction_UUID
        JOIN `{DS}.Recipe_BOM_Mapping` rbm ON li.Item_SKU = rbm.Sales_Item_SKU
        JOIN `{DS}.Inventory_Item_Master` inv ON rbm.Inventory_ID = inv.Inventory_ID
        WHERE t.Store_ID = @store_id
          AND t.Business_Date = @target_date
          AND t.Is_Voided = FALSE
        GROUP BY inv.Inventory_ID, inv.Description, inv.Category, inv.Recipe_UOM,
                 inv.Unit_Cost, inv.Count_UOM, inv.Conversion_Factor
        ORDER BY total_quantity_used DESC
    """, {"store_id": store_id, "target_date": target_date})

    usage_list = []
    for r in results:
        # Calculate cost: convert recipe units back to purchase units, then multiply by unit cost
        conversion = float(r["Conversion_Factor"]) if r["Conversion_Factor"] else 1
        quantity_in_purchase_units = float(r["total_quantity_used"]) / conversion if conversion > 0 else 0
        cost = quantity_in_purchase_units * float(r["Unit_Cost"]) if r["Unit_Cost"] else 0

        usage_list.append({
            "inventory_id": r["Inventory_ID"],
            "ingredient_name": r["ingredient_name"],
            "category": r["Category"],
            "quantity_used": round(float(r["total_quantity_used"]), 2),
            "unit": r["unit"],
            "cost": round(cost, 2)
        })

    return usage_list


@router.get("/cogs")
async def get_cogs_summary(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get cost of goods sold summary for the day."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Get total revenue
    revenue = db.query_one(f"""
        SELECT COALESCE(SUM(Total_Amount), 0) as total_revenue
        FROM `{DS}.Sales_Transactions_Header`
        WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
    """, {"store_id": store_id, "target_date": target_date})

    # Get COGS by category
    cogs_by_category = db.query(f"""
        SELECT
            inv.Category,
            SUM(li.Quantity * rbm.Quantity_Required * (1 + rbm.Yield_Loss_Pct) /
                NULLIF(inv.Conversion_Factor, 0) * inv.Unit_Cost) as category_cost
        FROM `{DS}.Sales_Order_Line_Items` li
        JOIN `{DS}.Sales_Transactions_Header` t ON li.Transaction_UUID = t.Transaction_UUID
        JOIN `{DS}.Recipe_BOM_Mapping` rbm ON li.Item_SKU = rbm.Sales_Item_SKU
        JOIN `{DS}.Inventory_Item_Master` inv ON rbm.Inventory_ID = inv.Inventory_ID
        WHERE t.Store_ID = @store_id
          AND t.Business_Date = @target_date
          AND t.Is_Voided = FALSE
        GROUP BY inv.Category
        ORDER BY category_cost DESC
    """, {"store_id": store_id, "target_date": target_date})

    total_cogs = sum(float(c["category_cost"] or 0) for c in cogs_by_category)
    total_rev = float(revenue["total_revenue"]) if revenue else 0
    cogs_pct = (total_cogs / total_rev * 100) if total_rev > 0 else 0

    return {
        "date": target_date,
        "total_revenue": round(total_rev, 2),
        "total_cogs": round(total_cogs, 2),
        "cogs_percentage": round(cogs_pct, 1),
        "gross_profit": round(total_rev - total_cogs, 2),
        "gross_margin": round(100 - cogs_pct, 1),
        "by_category": [
            {
                "category": c["Category"],
                "cost": round(float(c["category_cost"] or 0), 2),
                "percentage": round(float(c["category_cost"] or 0) / total_cogs * 100, 1) if total_cogs > 0 else 0
            }
            for c in cogs_by_category
        ]
    }


@router.get("/usage-by-category")
async def get_usage_by_category(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get ingredient usage grouped by category with top items."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Get totals by category
    categories = db.query(f"""
        SELECT
            inv.Category,
            COUNT(DISTINCT inv.Inventory_ID) as item_count,
            SUM(li.Quantity * rbm.Quantity_Required * (1 + rbm.Yield_Loss_Pct) /
                NULLIF(inv.Conversion_Factor, 0) * inv.Unit_Cost) as total_cost
        FROM `{DS}.Sales_Order_Line_Items` li
        JOIN `{DS}.Sales_Transactions_Header` t ON li.Transaction_UUID = t.Transaction_UUID
        JOIN `{DS}.Recipe_BOM_Mapping` rbm ON li.Item_SKU = rbm.Sales_Item_SKU
        JOIN `{DS}.Inventory_Item_Master` inv ON rbm.Inventory_ID = inv.Inventory_ID
        WHERE t.Store_ID = @store_id
          AND t.Business_Date = @target_date
          AND t.Is_Voided = FALSE
        GROUP BY inv.Category
        ORDER BY total_cost DESC
    """, {"store_id": store_id, "target_date": target_date})

    # Get top items per category
    result = []
    for cat in categories:
        items = db.query(f"""
            SELECT
                inv.Description as ingredient_name,
                inv.Recipe_UOM as unit,
                SUM(li.Quantity * rbm.Quantity_Required * (1 + rbm.Yield_Loss_Pct)) as quantity_used,
                SUM(li.Quantity * rbm.Quantity_Required * (1 + rbm.Yield_Loss_Pct) /
                    NULLIF(inv.Conversion_Factor, 0) * inv.Unit_Cost) as cost
            FROM `{DS}.Sales_Order_Line_Items` li
            JOIN `{DS}.Sales_Transactions_Header` t ON li.Transaction_UUID = t.Transaction_UUID
            JOIN `{DS}.Recipe_BOM_Mapping` rbm ON li.Item_SKU = rbm.Sales_Item_SKU
            JOIN `{DS}.Inventory_Item_Master` inv ON rbm.Inventory_ID = inv.Inventory_ID
            WHERE t.Store_ID = @store_id
              AND t.Business_Date = @target_date
              AND t.Is_Voided = FALSE
              AND inv.Category = @category
            GROUP BY inv.Description, inv.Recipe_UOM
            ORDER BY cost DESC
            LIMIT 5
        """, {"store_id": store_id, "target_date": target_date, "category": cat["Category"]})

        result.append({
            "category": cat["Category"],
            "item_count": cat["item_count"],
            "total_cost": round(float(cat["total_cost"] or 0), 2),
            "top_items": [
                {
                    "name": item["ingredient_name"],
                    "quantity": round(float(item["quantity_used"]), 2),
                    "unit": item["unit"],
                    "cost": round(float(item["cost"] or 0), 2)
                }
                for item in items
            ]
        })

    return result


@router.get("/top-cost-items")
async def get_top_cost_items(
    store_id: int = Query(1001),
    date: str = Query(None),
    limit: int = Query(10)
):
    """Get highest cost ingredients used today."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query(f"""
        SELECT
            inv.Description as ingredient_name,
            inv.Category,
            inv.Recipe_UOM as unit,
            SUM(li.Quantity * rbm.Quantity_Required * (1 + rbm.Yield_Loss_Pct)) as quantity_used,
            SUM(li.Quantity * rbm.Quantity_Required * (1 + rbm.Yield_Loss_Pct) /
                NULLIF(inv.Conversion_Factor, 0) * inv.Unit_Cost) as total_cost
        FROM `{DS}.Sales_Order_Line_Items` li
        JOIN `{DS}.Sales_Transactions_Header` t ON li.Transaction_UUID = t.Transaction_UUID
        JOIN `{DS}.Recipe_BOM_Mapping` rbm ON li.Item_SKU = rbm.Sales_Item_SKU
        JOIN `{DS}.Inventory_Item_Master` inv ON rbm.Inventory_ID = inv.Inventory_ID
        WHERE t.Store_ID = @store_id
          AND t.Business_Date = @target_date
          AND t.Is_Voided = FALSE
        GROUP BY inv.Description, inv.Category, inv.Recipe_UOM
        ORDER BY total_cost DESC
        LIMIT {limit}
    """, {"store_id": store_id, "target_date": target_date})

    return [
        {
            "rank": i + 1,
            "ingredient_name": r["ingredient_name"],
            "category": r["Category"],
            "quantity_used": round(float(r["quantity_used"]), 2),
            "unit": r["unit"],
            "total_cost": round(float(r["total_cost"] or 0), 2)
        }
        for i, r in enumerate(results)
    ]
