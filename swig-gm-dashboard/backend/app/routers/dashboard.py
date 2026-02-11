"""Dashboard KPI endpoints."""
from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from typing import List, Optional
import uuid
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

# Dataset prefix for BigQuery table references
DS = f"{settings.gcp_project_id}.{settings.bigquery_dataset}"


@router.get("/stores")
async def get_stores():
    """Get list of all stores."""
    db = get_db()
    results = db.query(f"""
        SELECT Store_ID, Store_Name, City, State
        FROM `{DS}.Organization_Stores`
        WHERE Is_Active = TRUE
        ORDER BY Store_ID
    """)
    return [
        {
            "store_id": r["Store_ID"],
            "store_name": r["Store_Name"],
            "city": r["City"],
            "state": r["State"]
        }
        for r in results
    ]


@router.get("/kpis")
async def get_kpis(
    store_id: int = Query(1001, description="Store ID"),
    date: str = Query(None, description="Date (YYYY-MM-DD)")
):
    """Get today's KPIs for a store."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Get transaction metrics
    tx_stats = db.query_one(f"""
        SELECT
            COUNT(*) as transaction_count,
            COALESCE(SUM(Total_Amount), 0) as total_revenue,
            COALESCE(AVG(Total_Amount), 0) as avg_ticket,
            COUNT(DISTINCT Employee_ID) as employees_sold
        FROM `{DS}.Sales_Transactions_Header`
        WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
    """, {"store_id": store_id, "target_date": target_date})

    # Get drive-thru throughput (peak hour)
    throughput = db.query_one(f"""
        SELECT
            EXTRACT(HOUR FROM Open_Timestamp) as peak_hour,
            COUNT(*) as peak_transactions
        FROM `{DS}.Sales_Transactions_Header`
        WHERE Store_ID = @store_id AND Business_Date = @target_date AND Service_Channel = 'Drive_Thru'
        GROUP BY EXTRACT(HOUR FROM Open_Timestamp)
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """, {"store_id": store_id, "target_date": target_date})

    # Get labor cost (simplified - actual hours * wage)
    labor = db.query_one(f"""
        SELECT
            COALESCE(SUM(t.Actual_Hours * e.Hourly_Wage), 0) as labor_cost
        FROM `{DS}.Time_Attendance_Actuals` t
        JOIN `{DS}.Employee_Master_Profile` e ON t.Employee_ID = e.Employee_ID
        WHERE t.Store_ID = @store_id AND t.Shift_Date = @target_date
    """, {"store_id": store_id, "target_date": target_date})

    labor_cost = labor["labor_cost"] if labor else 0
    revenue = tx_stats["total_revenue"] if tx_stats else 0
    labor_pct = (labor_cost / revenue * 100) if revenue > 0 else 0
    transactions = tx_stats["transaction_count"] if tx_stats else 0

    # Get comparison data using Python date math
    end_date = datetime.strptime(target_date, "%Y-%m-%d")
    yesterday_str = (end_date - timedelta(days=1)).strftime("%Y-%m-%d")
    last_week_str = (end_date - timedelta(days=7)).strftime("%Y-%m-%d")

    yesterday = db.query_one(f"""
        SELECT COUNT(*) as transactions, COALESCE(SUM(Total_Amount), 0) as revenue
        FROM `{DS}.Sales_Transactions_Header`
        WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
    """, {"store_id": store_id, "target_date": yesterday_str})

    last_week = db.query_one(f"""
        SELECT COUNT(*) as transactions, COALESCE(SUM(Total_Amount), 0) as revenue
        FROM `{DS}.Sales_Transactions_Header`
        WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
    """, {"store_id": store_id, "target_date": last_week_str})

    def calc_change(current, previous):
        if previous and previous > 0:
            return round((current - previous) / previous * 100, 1)
        return 0.0

    return {
        "date": target_date,
        "store_id": store_id,
        "transactions": transactions,
        "revenue": round(float(revenue), 2),
        "avg_ticket": round(float(tx_stats["avg_ticket"]), 2) if tx_stats else 0,
        "throughput": throughput["peak_transactions"] if throughput else 0,
        "labor_percentage": round(float(labor_pct), 1),
        "vs_yesterday": {
            "transactions": calc_change(transactions, yesterday["transactions"] if yesterday else 0),
            "revenue": calc_change(revenue, yesterday["revenue"] if yesterday else 0)
        },
        "vs_last_week": {
            "transactions": calc_change(transactions, last_week["transactions"] if last_week else 0),
            "revenue": calc_change(revenue, last_week["revenue"] if last_week else 0)
        }
    }


@router.get("/hourly")
async def get_hourly_breakdown(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get hour-by-hour transaction breakdown."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query(f"""
        SELECT
            EXTRACT(HOUR FROM Open_Timestamp) as hour,
            COUNT(*) as transactions,
            COALESCE(SUM(Total_Amount), 0) as revenue,
            COALESCE(AVG(Total_Amount), 0) as avg_ticket
        FROM `{DS}.Sales_Transactions_Header`
        WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
        GROUP BY EXTRACT(HOUR FROM Open_Timestamp)
        ORDER BY hour
    """, {"store_id": store_id, "target_date": target_date})

    # Find peak hour
    peak_transactions = max((r["transactions"] for r in results), default=0)

    return [
        {
            "hour": int(r["hour"]),
            "hour_label": f"{int(r['hour']):02d}:00 - {int(r['hour'])+1:02d}:00",
            "transactions": r["transactions"],
            "revenue": round(float(r["revenue"]), 2),
            "avg_ticket": round(float(r["avg_ticket"]), 2),
            "is_peak": r["transactions"] == peak_transactions and peak_transactions > 0
        }
        for r in results
    ]


@router.get("/alerts")
async def get_alerts(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get proactive alerts for the store."""
    db = get_db()
    target_date = date or settings.data_current_date
    alerts = []

    # Check for compliance violations today
    violations = db.query(f"""
        SELECT
            v.Violation_Type,
            v.Description,
            e.First_Name,
            e.Last_Name,
            e.Is_Minor
        FROM `{DS}.Labor_Compliance_Violations` v
        JOIN `{DS}.Employee_Master_Profile` e ON v.Employee_ID = e.Employee_ID
        WHERE v.Store_ID = @store_id AND v.Violation_Date = @target_date AND v.Resolved = FALSE
        ORDER BY
            CASE WHEN e.Is_Minor THEN 0 ELSE 1 END,
            v.Violation_Date DESC
        LIMIT 5
    """, {"store_id": store_id, "target_date": target_date})

    for v in violations:
        severity = "high" if v["Is_Minor"] else "medium"
        alerts.append({
            "id": str(uuid.uuid4()),
            "type": severity,
            "category": "compliance",
            "title": v["Violation_Type"].replace("_", " "),
            "description": f"{v['First_Name']} {v['Last_Name'][0]}. - {v['Description']}",
            "employee_name": f"{v['First_Name']} {v['Last_Name'][0]}."
        })

    # Check for minors working long shifts
    minor_hours = db.query(f"""
        SELECT
            e.First_Name,
            e.Last_Name,
            t.Actual_Hours,
            t.Break_Start
        FROM `{DS}.Time_Attendance_Actuals` t
        JOIN `{DS}.Employee_Master_Profile` e ON t.Employee_ID = e.Employee_ID
        WHERE t.Store_ID = @store_id
          AND t.Shift_Date = @target_date
          AND e.Is_Minor = TRUE
          AND t.Actual_Hours >= 3.5
          AND t.Break_Start IS NULL
    """, {"store_id": store_id, "target_date": target_date})

    for m in minor_hours:
        alerts.append({
            "id": str(uuid.uuid4()),
            "type": "high",
            "category": "labor",
            "title": "Minor Break Required",
            "description": f"{m['First_Name']} {m['Last_Name'][0]}. ({float(m['Actual_Hours']):.1f} hrs) needs a break soon",
            "employee_name": f"{m['First_Name']} {m['Last_Name'][0]}."
        })

    return alerts


@router.get("/comparison")
async def get_comparison(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Compare today's performance to yesterday and last week."""
    db = get_db()
    target_date = date or settings.data_current_date

    def get_day_stats(d: str):
        return db.query_one(f"""
            SELECT
                COUNT(*) as transactions,
                COALESCE(SUM(Total_Amount), 0) as revenue
            FROM `{DS}.Sales_Transactions_Header`
            WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
        """, {"store_id": store_id, "target_date": d})

    today = get_day_stats(target_date)

    # Calculate dates using Python
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    yesterday_str = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
    last_week_str = (dt - timedelta(days=7)).strftime("%Y-%m-%d")

    yesterday = get_day_stats(yesterday_str)
    last_week = get_day_stats(last_week_str)

    def calc_change(current, previous):
        if previous and previous > 0:
            return round((current - previous) / previous * 100, 1)
        return 0

    return {
        "today": {
            "transactions": today["transactions"] if today else 0,
            "revenue": round(float(today["revenue"]), 2) if today else 0
        },
        "vs_yesterday": {
            "transactions": yesterday["transactions"] if yesterday else 0,
            "revenue": round(float(yesterday["revenue"]), 2) if yesterday else 0,
            "transactions_change": calc_change(
                today["transactions"] if today else 0,
                yesterday["transactions"] if yesterday else 0
            ),
            "revenue_change": calc_change(
                float(today["revenue"]) if today else 0,
                float(yesterday["revenue"]) if yesterday else 0
            )
        },
        "vs_last_week": {
            "transactions": last_week["transactions"] if last_week else 0,
            "revenue": round(float(last_week["revenue"]), 2) if last_week else 0,
            "transactions_change": calc_change(
                today["transactions"] if today else 0,
                last_week["transactions"] if last_week else 0
            ),
            "revenue_change": calc_change(
                float(today["revenue"]) if today else 0,
                float(last_week["revenue"]) if last_week else 0
            )
        }
    }
