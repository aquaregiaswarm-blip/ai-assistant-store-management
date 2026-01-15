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
