"""Transaction query endpoints."""
from fastapi import APIRouter, Query
from typing import Optional
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/summary")
async def get_transaction_summary(
    store_id: int = Query(1001),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    """Get transaction summary for a date range."""
    db = get_db()
    end = end_date or settings.data_current_date
    start = start_date or end  # Default to single day

    return db.query_one("""
        SELECT
            COUNT(*) as total_transactions,
            COALESCE(SUM(Total_Amount), 0) as total_revenue,
            COALESCE(AVG(Total_Amount), 0) as avg_ticket,
            COUNT(DISTINCT Business_Date) as days,
            COUNT(DISTINCT Employee_ID) as unique_employees,
            SUM(CASE WHEN Service_Channel = 'Drive_Thru' THEN 1 ELSE 0 END) as drive_thru_count,
            SUM(CASE WHEN Service_Channel = 'Walk_Up' THEN 1 ELSE 0 END) as walk_up_count,
            SUM(CASE WHEN Service_Channel = 'Mobile_Pickup' THEN 1 ELSE 0 END) as mobile_count,
            SUM(CASE WHEN Customer_Loyalty_ID IS NOT NULL THEN 1 ELSE 0 END) as loyalty_identified
        FROM Sales_Transactions_Header
        WHERE Store_ID = ?
          AND Business_Date BETWEEN ? AND ?
          AND Is_Voided = false
    """, [store_id, start, end])


@router.get("/peak-hours")
async def get_peak_hours(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get peak hour analysis."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query("""
        SELECT
            EXTRACT(hour FROM Open_Timestamp) as hour,
            COUNT(*) as transactions,
            SUM(Total_Amount) as revenue,
            AVG(Total_Amount) as avg_ticket,
            SUM(CASE WHEN Service_Channel = 'Drive_Thru' THEN 1 ELSE 0 END) as drive_thru
        FROM Sales_Transactions_Header
        WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
        GROUP BY EXTRACT(hour FROM Open_Timestamp)
        ORDER BY transactions DESC
    """, [store_id, target_date])

    return [
        {
            "hour": int(r["hour"]),
            "hour_label": f"{int(r['hour']):02d}:00 - {int(r['hour'])+1:02d}:00",
            "transactions": r["transactions"],
            "revenue": round(r["revenue"], 2),
            "avg_ticket": round(r["avg_ticket"], 2),
            "drive_thru_pct": round(r["drive_thru"] / r["transactions"] * 100, 1) if r["transactions"] > 0 else 0,
            "is_peak": r == results[0] if results else False
        }
        for r in results
    ]


@router.get("/top-items")
async def get_top_items(
    store_id: int = Query(1001),
    date: str = Query(None),
    limit: int = Query(10),
    item_type: Optional[str] = Query(None, description="Filter by item type: Base_Beverage, Food, Modifier")
):
    """Get top selling items."""
    db = get_db()
    target_date = date or settings.data_current_date

    type_filter = ""
    params = [store_id, target_date]
    if item_type:
        type_filter = "AND li.Item_Type = ?"
        params.append(item_type)

    results = db.query(f"""
        SELECT
            li.Item_Name,
            li.Item_Type,
            COUNT(*) as quantity_sold,
            SUM(li.Unit_Price * li.Quantity) as revenue
        FROM Sales_Order_Line_Items li
        JOIN Sales_Transactions_Header t ON li.Transaction_UUID = t.Transaction_UUID
        WHERE t.Store_ID = ?
          AND t.Business_Date = ?
          AND t.Is_Voided = false
          {type_filter}
        GROUP BY li.Item_Name, li.Item_Type
        ORDER BY quantity_sold DESC
        LIMIT {limit}
    """, params)

    return [
        {
            "rank": i + 1,
            "item_name": r["Item_Name"],
            "item_type": r["Item_Type"],
            "quantity_sold": r["quantity_sold"],
            "revenue": round(r["revenue"], 2)
        }
        for i, r in enumerate(results)
    ]


@router.get("/by-channel")
async def get_by_channel(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get transaction breakdown by service channel."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query("""
        SELECT
            Service_Channel,
            COUNT(*) as transactions,
            SUM(Total_Amount) as revenue,
            AVG(Total_Amount) as avg_ticket
        FROM Sales_Transactions_Header
        WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
        GROUP BY Service_Channel
        ORDER BY transactions DESC
    """, [store_id, target_date])

    total = sum(r["transactions"] for r in results)

    return [
        {
            "channel": r["Service_Channel"],
            "transactions": r["transactions"],
            "percentage": round(r["transactions"] / total * 100, 1) if total > 0 else 0,
            "revenue": round(r["revenue"], 2),
            "avg_ticket": round(r["avg_ticket"], 2)
        }
        for r in results
    ]


@router.get("/hourly-detail/{hour}")
async def get_hourly_detail(
    hour: int,
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get detailed breakdown for a specific hour."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Transaction metrics for this hour
    tx_stats = db.query_one("""
        SELECT
            COUNT(*) as transaction_count,
            COALESCE(SUM(Total_Amount), 0) as revenue,
            COALESCE(AVG(Total_Amount), 0) as avg_ticket
        FROM Sales_Transactions_Header
        WHERE Store_ID = ?
          AND Business_Date = ?
          AND EXTRACT(hour FROM Open_Timestamp) = ?
          AND Is_Voided = false
    """, [store_id, target_date, hour])

    # Staff working during this hour
    staff = db.query("""
        SELECT DISTINCT
            e.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Role_Code,
            t.Clock_In_Time,
            t.Clock_Out_Time
        FROM Time_Attendance_Actuals t
        JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
        WHERE t.Store_ID = ?
          AND t.Shift_Date = ?
          AND t.Clock_In_Time IS NOT NULL
          AND EXTRACT(hour FROM t.Clock_In_Time) <= ?
          AND (t.Clock_Out_Time IS NULL OR EXTRACT(hour FROM t.Clock_Out_Time) >= ?)
    """, [store_id, target_date, hour, hour])

    # Top items sold this hour
    top_items = db.query("""
        SELECT
            li.Item_Name,
            li.Item_Type,
            SUM(li.Quantity) as quantity,
            SUM(li.Line_Total) as revenue
        FROM Sales_Order_Line_Items li
        JOIN Sales_Transactions_Header t ON li.Transaction_UUID = t.Transaction_UUID
        WHERE t.Store_ID = ?
          AND t.Business_Date = ?
          AND EXTRACT(hour FROM t.Open_Timestamp) = ?
          AND t.Is_Voided = false
          AND li.Item_Type = 'Base_Beverage'
        GROUP BY li.Item_Name, li.Item_Type
        ORDER BY quantity DESC
        LIMIT 5
    """, [store_id, target_date, hour])

    # Service channel breakdown
    channels = db.query("""
        SELECT
            Service_Channel,
            COUNT(*) as count,
            SUM(Total_Amount) as revenue
        FROM Sales_Transactions_Header
        WHERE Store_ID = ?
          AND Business_Date = ?
          AND EXTRACT(hour FROM Open_Timestamp) = ?
          AND Is_Voided = false
        GROUP BY Service_Channel
    """, [store_id, target_date, hour])

    total_tx = tx_stats["transaction_count"] if tx_stats else 0

    # Drive-thru speed for this hour
    dt_speed = db.query_one("""
        SELECT
            AVG(Duration_Seconds) as avg_seconds,
            COUNT(*) as car_count
        FROM Drive_Thru_Loop_Metrics
        WHERE Store_ID = ?
          AND Business_Date = ?
          AND EXTRACT(hour FROM Arrival_Time) = ?
          AND Sensor_ID = 'Window'
    """, [store_id, target_date, hour])

    # Labor cost for this hour (approximate)
    labor = db.query_one("""
        SELECT
            COUNT(DISTINCT t.Employee_ID) as staff_count,
            SUM(e.Hourly_Wage) as hourly_labor_cost
        FROM Time_Attendance_Actuals t
        JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
        WHERE t.Store_ID = ?
          AND t.Shift_Date = ?
          AND t.Clock_In_Time IS NOT NULL
          AND EXTRACT(hour FROM t.Clock_In_Time) <= ?
          AND (t.Clock_Out_Time IS NULL OR EXTRACT(hour FROM t.Clock_Out_Time) >= ?)
    """, [store_id, target_date, hour, hour])

    return {
        "hour": hour,
        "hour_label": f"{hour:02d}:00 - {hour+1:02d}:00",
        "date": target_date,
        "transactions": {
            "count": tx_stats["transaction_count"] if tx_stats else 0,
            "revenue": round(float(tx_stats["revenue"]), 2) if tx_stats else 0,
            "avg_ticket": round(float(tx_stats["avg_ticket"]), 2) if tx_stats else 0
        },
        "staff": [
            {
                "employee_id": s["Employee_ID"],
                "name": f"{s['First_Name']} {s['Last_Name']}",
                "role": s["Role_Code"]
            }
            for s in staff
        ],
        "top_items": [
            {
                "name": item["Item_Name"],
                "quantity": item["quantity"],
                "revenue": round(float(item["revenue"]), 2)
            }
            for item in top_items
        ],
        "channels": [
            {
                "channel": c["Service_Channel"],
                "count": c["count"],
                "percentage": round(c["count"] / total_tx * 100, 1) if total_tx > 0 else 0,
                "revenue": round(float(c["revenue"]), 2)
            }
            for c in channels
        ],
        "drive_thru": {
            "avg_service_seconds": round(float(dt_speed["avg_seconds"]), 0) if dt_speed and dt_speed["avg_seconds"] else None,
            "cars_served": dt_speed["car_count"] if dt_speed else 0
        },
        "labor": {
            "staff_count": labor["staff_count"] if labor else 0,
            "hourly_cost": round(float(labor["hourly_labor_cost"]), 2) if labor and labor["hourly_labor_cost"] else 0
        }
    }


@router.get("/sales-by-category")
async def get_sales_by_category(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get sales grouped by product category."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Get category breakdown
    categories = db.query("""
        SELECT
            pc.Category_Name,
            COUNT(DISTINCT li.Transaction_UUID) as transaction_count,
            SUM(li.Quantity) as quantity_sold,
            SUM(li.Line_Total) as revenue
        FROM Sales_Order_Line_Items li
        JOIN Sales_Transactions_Header t ON li.Transaction_UUID = t.Transaction_UUID
        JOIN Product_Catalog p ON li.Item_SKU = p.Item_SKU
        JOIN Product_Categories pc ON p.Category_ID = pc.Category_ID
        WHERE t.Store_ID = ?
          AND t.Business_Date = ?
          AND t.Is_Voided = false
        GROUP BY pc.Category_ID, pc.Category_Name
        ORDER BY revenue DESC
    """, [store_id, target_date])

    total_revenue = sum(float(c["revenue"] or 0) for c in categories)

    # Get item type breakdown (Base_Beverage, Modifier, Food, etc.)
    item_types = db.query("""
        SELECT
            li.Item_Type,
            SUM(li.Quantity) as quantity,
            SUM(li.Line_Total) as revenue
        FROM Sales_Order_Line_Items li
        JOIN Sales_Transactions_Header t ON li.Transaction_UUID = t.Transaction_UUID
        WHERE t.Store_ID = ?
          AND t.Business_Date = ?
          AND t.Is_Voided = false
        GROUP BY li.Item_Type
        ORDER BY revenue DESC
    """, [store_id, target_date])

    return {
        "date": target_date,
        "total_revenue": round(total_revenue, 2),
        "by_category": [
            {
                "category": c["Category_Name"],
                "transaction_count": c["transaction_count"],
                "quantity_sold": c["quantity_sold"],
                "revenue": round(float(c["revenue"] or 0), 2),
                "percentage": round(float(c["revenue"] or 0) / total_revenue * 100, 1) if total_revenue > 0 else 0
            }
            for c in categories
        ],
        "by_item_type": [
            {
                "type": it["Item_Type"],
                "quantity": it["quantity"],
                "revenue": round(float(it["revenue"] or 0), 2)
            }
            for it in item_types
        ]
    }


@router.get("/payment-breakdown")
async def get_payment_breakdown(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get payment method distribution."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query("""
        SELECT
            p.Tender_Type,
            COUNT(*) as transaction_count,
            SUM(p.Amount_Tendered) as total_amount,
            SUM(p.Tip_Amount) as total_tips,
            AVG(p.Amount_Tendered) as avg_amount
        FROM Sales_Payments p
        JOIN Sales_Transactions_Header t ON p.Transaction_UUID = t.Transaction_UUID
        WHERE t.Store_ID = ?
          AND t.Business_Date = ?
          AND t.Is_Voided = false
        GROUP BY p.Tender_Type
        ORDER BY transaction_count DESC
    """, [store_id, target_date])

    total_tx = sum(r["transaction_count"] for r in results)
    total_amount = sum(float(r["total_amount"] or 0) for r in results)
    total_tips = sum(float(r["total_tips"] or 0) for r in results)

    return {
        "date": target_date,
        "summary": {
            "total_transactions": total_tx,
            "total_amount": round(total_amount, 2),
            "total_tips": round(total_tips, 2),
            "tip_percentage": round(total_tips / (total_amount - total_tips) * 100, 1) if (total_amount - total_tips) > 0 else 0
        },
        "by_method": [
            {
                "method": r["Tender_Type"],
                "transaction_count": r["transaction_count"],
                "percentage": round(r["transaction_count"] / total_tx * 100, 1) if total_tx > 0 else 0,
                "total_amount": round(float(r["total_amount"] or 0), 2),
                "tips": round(float(r["total_tips"] or 0), 2),
                "avg_amount": round(float(r["avg_amount"] or 0), 2)
            }
            for r in results
        ]
    }


@router.get("/loyalty-stats")
async def get_loyalty_stats(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get loyalty program statistics."""
    db = get_db()
    target_date = date or settings.data_current_date

    stats = db.query_one("""
        SELECT
            COUNT(*) as total_transactions,
            SUM(CASE WHEN Customer_Loyalty_ID IS NOT NULL THEN 1 ELSE 0 END) as loyalty_transactions,
            SUM(CASE WHEN Customer_Loyalty_ID IS NOT NULL THEN Total_Amount ELSE 0 END) as loyalty_revenue,
            SUM(CASE WHEN Customer_Loyalty_ID IS NULL THEN Total_Amount ELSE 0 END) as non_loyalty_revenue,
            AVG(CASE WHEN Customer_Loyalty_ID IS NOT NULL THEN Total_Amount END) as loyalty_avg_ticket,
            AVG(CASE WHEN Customer_Loyalty_ID IS NULL THEN Total_Amount END) as non_loyalty_avg_ticket
        FROM Sales_Transactions_Header
        WHERE Store_ID = ?
          AND Business_Date = ?
          AND Is_Voided = false
    """, [store_id, target_date])

    total_tx = stats["total_transactions"] if stats else 0
    loyalty_tx = stats["loyalty_transactions"] if stats else 0

    return {
        "date": target_date,
        "total_transactions": total_tx,
        "loyalty": {
            "transactions": loyalty_tx,
            "percentage": round(loyalty_tx / total_tx * 100, 1) if total_tx > 0 else 0,
            "revenue": round(float(stats["loyalty_revenue"] or 0), 2) if stats else 0,
            "avg_ticket": round(float(stats["loyalty_avg_ticket"] or 0), 2) if stats else 0
        },
        "non_loyalty": {
            "transactions": total_tx - loyalty_tx,
            "percentage": round((total_tx - loyalty_tx) / total_tx * 100, 1) if total_tx > 0 else 0,
            "revenue": round(float(stats["non_loyalty_revenue"] or 0), 2) if stats else 0,
            "avg_ticket": round(float(stats["non_loyalty_avg_ticket"] or 0), 2) if stats else 0
        }
    }


@router.get("/linebuster-stats")
async def get_linebuster_stats(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Analyze linebuster effectiveness via queue position distribution."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Queue position distribution
    queue_dist = db.query("""
        SELECT
            Queue_Position,
            COUNT(*) as count
        FROM Sales_Transactions_Header
        WHERE Store_ID = ?
          AND Business_Date = ?
          AND Service_Channel = 'Drive_Thru'
          AND Queue_Position IS NOT NULL
        GROUP BY Queue_Position
        ORDER BY Queue_Position
    """, [store_id, target_date])

    # Average queue position by hour
    hourly_queue = db.query("""
        SELECT
            EXTRACT(hour FROM Open_Timestamp) as hour,
            AVG(Queue_Position) as avg_queue_position,
            COUNT(*) as drive_thru_count
        FROM Sales_Transactions_Header
        WHERE Store_ID = ?
          AND Business_Date = ?
          AND Service_Channel = 'Drive_Thru'
          AND Queue_Position IS NOT NULL
        GROUP BY EXTRACT(hour FROM Open_Timestamp)
        ORDER BY hour
    """, [store_id, target_date])

    total_dt = sum(r["count"] for r in queue_dist)
    linebuster_orders = sum(r["count"] for r in queue_dist if r["Queue_Position"] > 2)

    return {
        "total_drive_thru": total_dt,
        "linebuster_orders": linebuster_orders,
        "linebuster_pct": round(linebuster_orders / total_dt * 100, 1) if total_dt > 0 else 0,
        "avg_queue_position": round(sum(r["Queue_Position"] * r["count"] for r in queue_dist) / total_dt, 1) if total_dt > 0 else 0,
        "queue_distribution": [
            {"position": r["Queue_Position"], "count": r["count"]}
            for r in queue_dist
        ],
        "hourly_avg": [
            {
                "hour": int(r["hour"]),
                "avg_position": round(r["avg_queue_position"], 1),
                "count": r["drive_thru_count"]
            }
            for r in hourly_queue
        ]
    }
