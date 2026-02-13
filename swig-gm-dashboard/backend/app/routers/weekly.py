"""Weekly summary and trends endpoints."""
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/weekly", tags=["weekly"])


def get_week_bounds(target_date: str):
    """Get Monday-Sunday bounds for the week containing target_date."""
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    # Monday of the week
    week_start = dt - timedelta(days=dt.weekday())
    # Sunday of the week
    week_end = week_start + timedelta(days=6)
    return week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")


@router.get("/summary")
async def get_weekly_summary(
    store_id: int = Query(1001),
    date: str = Query(None, description="Any date within the desired week")
):
    """Get weekly aggregate metrics."""
    db = get_db()
    target_date = date or settings.data_current_date
    week_start, week_end = get_week_bounds(target_date)

    # Transaction metrics
    tx_stats = db.query_one("""
        SELECT
            COUNT(*) as transaction_count,
            COALESCE(SUM("Total_Amount"), 0) as total_revenue,
            COALESCE(AVG("Total_Amount"), 0) as avg_ticket,
            COUNT(DISTINCT "Business_Date") as days_with_sales,
            COUNT(DISTINCT "Employee_ID") as unique_employees,
            SUM(CASE WHEN "Customer_Loyalty_ID" IS NOT NULL THEN 1 ELSE 0 END) as loyalty_transactions
        FROM "Sales_Transactions_Header"
        WHERE "Store_ID" = %(store_id)s
          AND "Business_Date" BETWEEN %(week_start)s AND %(week_end)s
          AND "Is_Voided" = false
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    # Labor metrics
    labor = db.query_one("""
        SELECT
            COALESCE(SUM(t."Actual_Hours"), 0) as total_hours,
            COALESCE(SUM(t."Actual_Hours" * e."Hourly_Wage"), 0) as total_labor_cost,
            COUNT(DISTINCT t."Employee_ID") as employees_worked
        FROM "Time_Attendance_Actuals" t
        JOIN "Employee_Master_Profile" e ON t."Employee_ID" = e."Employee_ID"
        WHERE t."Store_ID" = %(store_id)s
          AND t."Shift_Date" BETWEEN %(week_start)s AND %(week_end)s
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    # Compliance violations
    violations = db.query_one("""
        SELECT
            COUNT(*) as violation_count,
            COALESCE(SUM("Penalty_Cost"), 0) as total_penalties
        FROM "Labor_Compliance_Violations"
        WHERE "Store_ID" = %(store_id)s
          AND "Violation_Date" BETWEEN %(week_start)s AND %(week_end)s
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    # Top items for the week
    top_items = db.query("""
        SELECT
            li."Item_Name",
            li."Item_Type",
            SUM(li."Quantity") as quantity_sold,
            SUM(li."Line_Total") as revenue
        FROM "Sales_Order_Line_Items" li
        JOIN "Sales_Transactions_Header" t ON li."Transaction_UUID" = t."Transaction_UUID"
        WHERE t."Store_ID" = %(store_id)s
          AND t."Business_Date" BETWEEN %(week_start)s AND %(week_end)s
          AND t."Is_Voided" = false
          AND li."Item_Type" = 'Base_Beverage'
        GROUP BY li."Item_Name", li."Item_Type"
        ORDER BY quantity_sold DESC
        LIMIT 5
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    revenue = float(tx_stats["total_revenue"]) if tx_stats else 0
    labor_cost = float(labor["total_labor_cost"]) if labor else 0
    labor_pct = (labor_cost / revenue * 100) if revenue > 0 else 0

    return {
        "week_start": week_start,
        "week_end": week_end,
        "store_id": store_id,
        "sales": {
            "total_revenue": round(revenue, 2),
            "transaction_count": tx_stats["transaction_count"] if tx_stats else 0,
            "avg_ticket": round(float(tx_stats["avg_ticket"]), 2) if tx_stats else 0,
            "days_with_sales": tx_stats["days_with_sales"] if tx_stats else 0,
            "loyalty_transactions": tx_stats["loyalty_transactions"] if tx_stats else 0,
            "loyalty_percentage": round(tx_stats["loyalty_transactions"] / tx_stats["transaction_count"] * 100, 1) if tx_stats and tx_stats["transaction_count"] > 0 else 0
        },
        "labor": {
            "total_hours": round(float(labor["total_hours"]), 1) if labor else 0,
            "total_cost": round(labor_cost, 2),
            "labor_percentage": round(labor_pct, 1),
            "employees_worked": labor["employees_worked"] if labor else 0
        },
        "compliance": {
            "violation_count": violations["violation_count"] if violations else 0,
            "total_penalties": round(float(violations["total_penalties"]), 2) if violations else 0
        },
        "top_items": [
            {
                "name": item["Item_Name"],
                "quantity": item["quantity_sold"],
                "revenue": round(float(item["revenue"]), 2)
            }
            for item in top_items
        ]
    }


@router.get("/trends")
async def get_weekly_trends(
    store_id: int = Query(1001),
    date: str = Query(None, description="Any date within the desired week")
):
    """Get day-by-day trends for the week."""
    db = get_db()
    target_date = date or settings.data_current_date
    week_start, week_end = get_week_bounds(target_date)

    # Daily revenue and transactions
    daily_sales = db.query("""
        SELECT
            "Business_Date",
            COUNT(*) as transactions,
            COALESCE(SUM("Total_Amount"), 0) as revenue,
            COALESCE(AVG("Total_Amount"), 0) as avg_ticket
        FROM "Sales_Transactions_Header"
        WHERE "Store_ID" = %(store_id)s
          AND "Business_Date" BETWEEN %(week_start)s AND %(week_end)s
          AND "Is_Voided" = false
        GROUP BY "Business_Date"
        ORDER BY "Business_Date"
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    # Daily labor costs
    daily_labor = db.query("""
        SELECT
            t."Shift_Date" as date,
            COALESCE(SUM(t."Actual_Hours"), 0) as hours,
            COALESCE(SUM(t."Actual_Hours" * e."Hourly_Wage"), 0) as labor_cost
        FROM "Time_Attendance_Actuals" t
        JOIN "Employee_Master_Profile" e ON t."Employee_ID" = e."Employee_ID"
        WHERE t."Store_ID" = %(store_id)s
          AND t."Shift_Date" BETWEEN %(week_start)s AND %(week_end)s
        GROUP BY t."Shift_Date"
        ORDER BY t."Shift_Date"
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    # Create lookup for labor data
    labor_by_date = {str(l["date"])[:10]: l for l in daily_labor}

    # Build combined daily data
    daily_data = []
    for day in daily_sales:
        date_str = str(day["Business_Date"])[:10]
        labor = labor_by_date.get(date_str, {})
        revenue = float(day["revenue"])
        labor_cost = float(labor.get("labor_cost", 0))

        daily_data.append({
            "date": date_str,
            "day_name": datetime.strptime(date_str, "%Y-%m-%d").strftime("%A"),
            "transactions": day["transactions"],
            "revenue": round(revenue, 2),
            "avg_ticket": round(float(day["avg_ticket"]), 2),
            "labor_hours": round(float(labor.get("hours", 0)), 1),
            "labor_cost": round(labor_cost, 2),
            "labor_percentage": round(labor_cost / revenue * 100, 1) if revenue > 0 else 0
        })

    return {
        "week_start": week_start,
        "week_end": week_end,
        "daily": daily_data
    }


@router.get("/comparison")
async def get_week_over_week(
    store_id: int = Query(1001),
    date: str = Query(None, description="Any date within the current week")
):
    """Compare current week to previous week."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Current week bounds
    curr_start, curr_end = get_week_bounds(target_date)

    # Previous week bounds
    prev_date = (datetime.strptime(curr_start, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    prev_start, prev_end = get_week_bounds(prev_date)

    def get_week_stats(start: str, end: str):
        sales = db.query_one("""
            SELECT
                COUNT(*) as transactions,
                COALESCE(SUM("Total_Amount"), 0) as revenue,
                COALESCE(AVG("Total_Amount"), 0) as avg_ticket
            FROM "Sales_Transactions_Header"
            WHERE "Store_ID" = %(store_id)s
              AND "Business_Date" BETWEEN %(start)s AND %(end)s
              AND "Is_Voided" = false
        """, {"store_id": store_id, "start": start, "end": end})

        labor = db.query_one("""
            SELECT
                COALESCE(SUM(t."Actual_Hours" * e."Hourly_Wage"), 0) as labor_cost
            FROM "Time_Attendance_Actuals" t
            JOIN "Employee_Master_Profile" e ON t."Employee_ID" = e."Employee_ID"
            WHERE t."Store_ID" = %(store_id)s
              AND t."Shift_Date" BETWEEN %(start)s AND %(end)s
        """, {"store_id": store_id, "start": start, "end": end})

        return {
            "transactions": sales["transactions"] if sales else 0,
            "revenue": round(float(sales["revenue"]), 2) if sales else 0,
            "avg_ticket": round(float(sales["avg_ticket"]), 2) if sales else 0,
            "labor_cost": round(float(labor["labor_cost"]), 2) if labor else 0
        }

    current = get_week_stats(curr_start, curr_end)
    previous = get_week_stats(prev_start, prev_end)

    def calc_change(curr, prev):
        if prev and prev > 0:
            return round((curr - prev) / prev * 100, 1)
        return 0.0

    return {
        "current_week": {
            "start": curr_start,
            "end": curr_end,
            **current
        },
        "previous_week": {
            "start": prev_start,
            "end": prev_end,
            **previous
        },
        "changes": {
            "transactions": calc_change(current["transactions"], previous["transactions"]),
            "revenue": calc_change(current["revenue"], previous["revenue"]),
            "avg_ticket": calc_change(current["avg_ticket"], previous["avg_ticket"]),
            "labor_cost": calc_change(current["labor_cost"], previous["labor_cost"])
        }
    }


@router.get("/cogs-summary")
async def get_weekly_cogs(
    store_id: int = Query(1001),
    date: str = Query(None, description="Any date within the desired week")
):
    """Get weekly COGS summary."""
    db = get_db()
    target_date = date or settings.data_current_date
    week_start, week_end = get_week_bounds(target_date)

    # Get revenue
    revenue = db.query_one("""
        SELECT COALESCE(SUM("Total_Amount"), 0) as total_revenue
        FROM "Sales_Transactions_Header"
        WHERE "Store_ID" = %(store_id)s AND "Business_Date" BETWEEN %(week_start)s AND %(week_end)s AND "Is_Voided" = false
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    # Get COGS by category
    cogs = db.query("""
        SELECT
            inv."Category",
            SUM(li."Quantity" * rbm."Quantity_Required" * (1 + rbm."Yield_Loss_Pct") /
                NULLIF(inv."Conversion_Factor", 0) * inv."Unit_Cost") as category_cost
        FROM "Sales_Order_Line_Items" li
        JOIN "Sales_Transactions_Header" t ON li."Transaction_UUID" = t."Transaction_UUID"
        JOIN "Recipe_BOM_Mapping" rbm ON li."Item_SKU" = rbm."Sales_Item_SKU"
        JOIN "Inventory_Item_Master" inv ON rbm."Inventory_ID" = inv."Inventory_ID"
        WHERE t."Store_ID" = %(store_id)s
          AND t."Business_Date" BETWEEN %(week_start)s AND %(week_end)s
          AND t."Is_Voided" = false
        GROUP BY inv."Category"
        ORDER BY category_cost DESC
    """, {"store_id": store_id, "week_start": week_start, "week_end": week_end})

    total_cogs = sum(float(c["category_cost"] or 0) for c in cogs)
    total_rev = float(revenue["total_revenue"]) if revenue else 0

    return {
        "week_start": week_start,
        "week_end": week_end,
        "total_revenue": round(total_rev, 2),
        "total_cogs": round(total_cogs, 2),
        "cogs_percentage": round(total_cogs / total_rev * 100, 1) if total_rev > 0 else 0,
        "gross_profit": round(total_rev - total_cogs, 2),
        "by_category": [
            {
                "category": c["Category"],
                "cost": round(float(c["category_cost"] or 0), 2)
            }
            for c in cogs
        ]
    }
