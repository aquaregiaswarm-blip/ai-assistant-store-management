"""Tool definitions and implementations for the GM AI Agent."""
from typing import Any, Dict, List
from ..database import get_db
from ..config import settings


# Tool definitions for Claude API
TOOL_DEFINITIONS = [
    {
        "name": "query_transactions",
        "description": "Query sales transaction data with flexible aggregation. Use this to answer questions about sales, revenue, transaction counts, and order patterns.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "integer",
                    "description": "Store ID to query"
                },
                "date": {
                    "type": "string",
                    "description": "Date to query in YYYY-MM-DD format"
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["daily", "hourly", "by_channel", "by_employee"],
                    "description": "How to aggregate the data"
                }
            },
            "required": ["store_id", "date"]
        }
    },
    {
        "name": "query_workforce",
        "description": "Query workforce and scheduling data. Use this for questions about who's working, schedules, attendance, and labor hours.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "integer",
                    "description": "Store ID to query"
                },
                "query_type": {
                    "type": "string",
                    "enum": ["schedule_today", "whos_working", "attendance", "minors"],
                    "description": "Type of workforce query"
                },
                "date": {
                    "type": "string",
                    "description": "Date to query in YYYY-MM-DD format"
                }
            },
            "required": ["store_id", "query_type", "date"]
        }
    },
    {
        "name": "check_compliance",
        "description": "Check for labor compliance issues including minor hours, break violations, and overtime risk. Use this when asked about compliance, violations, or employee issues.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "integer",
                    "description": "Store ID to query"
                },
                "check_type": {
                    "type": "string",
                    "enum": ["violations", "minor_status", "overtime_risk", "all"],
                    "description": "Type of compliance check"
                },
                "date": {
                    "type": "string",
                    "description": "Date to query in YYYY-MM-DD format"
                }
            },
            "required": ["store_id", "check_type", "date"]
        }
    },
    {
        "name": "compare_performance",
        "description": "Compare current performance to historical periods. Use this for questions like 'how did we do vs yesterday' or 'compared to last week'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "integer",
                    "description": "Store ID to query"
                },
                "date": {
                    "type": "string",
                    "description": "Date to compare from in YYYY-MM-DD format"
                },
                "comparison": {
                    "type": "string",
                    "enum": ["yesterday", "last_week", "same_day_last_week"],
                    "description": "What period to compare against"
                }
            },
            "required": ["store_id", "date", "comparison"]
        }
    },
    {
        "name": "get_top_items",
        "description": "Get the best-selling items. Use this for questions about popular items, top sellers, or menu performance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "integer",
                    "description": "Store ID to query"
                },
                "date": {
                    "type": "string",
                    "description": "Date to query in YYYY-MM-DD format"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of items to return (default 10)"
                },
                "item_type": {
                    "type": "string",
                    "enum": ["Base_Beverage", "Food", "Modifier", "all"],
                    "description": "Filter by item type"
                }
            },
            "required": ["store_id", "date"]
        }
    },
    {
        "name": "analyze_linebuster",
        "description": "Analyze linebuster effectiveness through queue position data. Use this for questions about drive-thru efficiency, linebuster performance, or queue management.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "integer",
                    "description": "Store ID to query"
                },
                "date": {
                    "type": "string",
                    "description": "Date to query in YYYY-MM-DD format"
                }
            },
            "required": ["store_id", "date"]
        }
    },
    {
        "name": "get_peak_hours",
        "description": "Get detailed peak hour analysis showing busiest times. Use this for questions about when the store is busiest or rush hour performance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "integer",
                    "description": "Store ID to query"
                },
                "date": {
                    "type": "string",
                    "description": "Date to query in YYYY-MM-DD format"
                }
            },
            "required": ["store_id", "date"]
        }
    }
]


def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool and return the result."""
    db = get_db()

    if tool_name == "query_transactions":
        return _query_transactions(db, tool_input)
    elif tool_name == "query_workforce":
        return _query_workforce(db, tool_input)
    elif tool_name == "check_compliance":
        return _check_compliance(db, tool_input)
    elif tool_name == "compare_performance":
        return _compare_performance(db, tool_input)
    elif tool_name == "get_top_items":
        return _get_top_items(db, tool_input)
    elif tool_name == "analyze_linebuster":
        return _analyze_linebuster(db, tool_input)
    elif tool_name == "get_peak_hours":
        return _get_peak_hours(db, tool_input)
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def _query_transactions(db, params: Dict) -> Dict:
    """Query transaction data."""
    store_id = params["store_id"]
    date = params["date"]
    aggregation = params.get("aggregation", "daily")

    if aggregation == "daily":
        result = db.query_one("""
            SELECT
                COUNT(*) as transactions,
                COALESCE(SUM(Total_Amount), 0) as revenue,
                COALESCE(AVG(Total_Amount), 0) as avg_ticket,
                COUNT(DISTINCT Employee_ID) as employees
            FROM Sales_Transactions_Header
            WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
        """, [store_id, date])
        return {
            "date": date,
            "transactions": result["transactions"],
            "revenue": round(result["revenue"], 2),
            "avg_ticket": round(result["avg_ticket"], 2),
            "employees_who_sold": result["employees"]
        }

    elif aggregation == "hourly":
        results = db.query("""
            SELECT
                EXTRACT(hour FROM Open_Timestamp) as hour,
                COUNT(*) as transactions,
                SUM(Total_Amount) as revenue
            FROM Sales_Transactions_Header
            WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
            GROUP BY EXTRACT(hour FROM Open_Timestamp)
            ORDER BY transactions DESC
        """, [store_id, date])
        return {
            "date": date,
            "hourly_breakdown": [
                {"hour": f"{int(r['hour']):02d}:00", "transactions": r["transactions"], "revenue": round(r["revenue"], 2)}
                for r in results
            ],
            "peak_hour": f"{int(results[0]['hour']):02d}:00" if results else None,
            "peak_transactions": results[0]["transactions"] if results else 0
        }

    elif aggregation == "by_channel":
        results = db.query("""
            SELECT
                Service_Channel as channel,
                COUNT(*) as transactions,
                SUM(Total_Amount) as revenue
            FROM Sales_Transactions_Header
            WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
            GROUP BY Service_Channel
            ORDER BY transactions DESC
        """, [store_id, date])
        total = sum(r["transactions"] for r in results)
        return {
            "date": date,
            "by_channel": [
                {
                    "channel": r["channel"],
                    "transactions": r["transactions"],
                    "percentage": round(r["transactions"] / total * 100, 1) if total > 0 else 0,
                    "revenue": round(r["revenue"], 2)
                }
                for r in results
            ]
        }

    elif aggregation == "by_employee":
        results = db.query("""
            SELECT
                e.First_Name,
                e.Last_Name,
                e.Role_Code,
                COUNT(*) as transactions,
                SUM(t.Total_Amount) as revenue
            FROM Sales_Transactions_Header t
            JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
            WHERE t.Store_ID = ? AND t.Business_Date = ? AND t.Is_Voided = false
            GROUP BY e.Employee_ID, e.First_Name, e.Last_Name, e.Role_Code
            ORDER BY transactions DESC
        """, [store_id, date])
        return {
            "date": date,
            "by_employee": [
                {
                    "name": f"{r['First_Name']} {r['Last_Name']}",
                    "role": r["Role_Code"],
                    "transactions": r["transactions"],
                    "revenue": round(r["revenue"], 2)
                }
                for r in results
            ]
        }

    return {"error": "Invalid aggregation type"}


def _query_workforce(db, params: Dict) -> Dict:
    """Query workforce data."""
    store_id = params["store_id"]
    query_type = params["query_type"]
    date = params["date"]

    if query_type == "schedule_today":
        results = db.query("""
            SELECT
                e.First_Name, e.Last_Name, e.Role_Code, e.Is_Minor,
                s.Shift_Start, s.Shift_End, s.Scheduled_Hours
            FROM Labor_Schedules_Published s
            JOIN Employee_Master_Profile e ON s.Employee_ID = e.Employee_ID
            WHERE s.Store_ID = ? AND s.Shift_Date = ?
            ORDER BY s.Shift_Start
        """, [store_id, date])
        return {
            "date": date,
            "scheduled_shifts": len(results),
            "schedule": [
                {
                    "name": f"{r['First_Name']} {r['Last_Name']}",
                    "role": r["Role_Code"],
                    "is_minor": r["Is_Minor"],
                    "start": str(r["Shift_Start"])[11:16],
                    "end": str(r["Shift_End"])[11:16],
                    "hours": float(r["Scheduled_Hours"])
                }
                for r in results
            ]
        }

    elif query_type == "whos_working":
        results = db.query("""
            SELECT
                e.First_Name, e.Last_Name, e.Role_Code, e.Is_Minor,
                t.Clock_In_Time, t.Actual_Hours, t.Break_Start
            FROM Time_Attendance_Actuals t
            JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
            WHERE t.Store_ID = ? AND t.Shift_Date = ? AND t.Is_No_Show = false
            ORDER BY t.Clock_In_Time
        """, [store_id, date])
        return {
            "date": date,
            "employees_working": len(results),
            "staff": [
                {
                    "name": f"{r['First_Name']} {r['Last_Name']}",
                    "role": r["Role_Code"],
                    "is_minor": r["Is_Minor"],
                    "clocked_in": str(r["Clock_In_Time"])[11:16] if r["Clock_In_Time"] else None,
                    "hours_worked": round(float(r["Actual_Hours"]), 1) if r["Actual_Hours"] else 0,
                    "has_taken_break": r["Break_Start"] is not None
                }
                for r in results
            ]
        }

    elif query_type == "attendance":
        late = db.query("""
            SELECT e.First_Name, e.Last_Name, t.Late_Minutes
            FROM Time_Attendance_Actuals t
            JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
            WHERE t.Store_ID = ? AND t.Shift_Date = ? AND t.Is_Late = true
        """, [store_id, date])

        no_shows = db.query("""
            SELECT e.First_Name, e.Last_Name
            FROM Time_Attendance_Actuals t
            JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
            WHERE t.Store_ID = ? AND t.Shift_Date = ? AND t.Is_No_Show = true
        """, [store_id, date])

        return {
            "date": date,
            "late_arrivals": [{"name": f"{r['First_Name']} {r['Last_Name']}", "minutes_late": r["Late_Minutes"]} for r in late],
            "no_shows": [f"{r['First_Name']} {r['Last_Name']}" for r in no_shows],
            "total_late": len(late),
            "total_no_shows": len(no_shows)
        }

    elif query_type == "minors":
        results = db.query("""
            SELECT
                e.First_Name, e.Last_Name,
                t.Clock_In_Time, t.Actual_Hours, t.Break_Start
            FROM Time_Attendance_Actuals t
            JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
            WHERE t.Store_ID = ? AND t.Shift_Date = ? AND e.Is_Minor = true AND t.Is_No_Show = false
        """, [store_id, date])
        return {
            "date": date,
            "minors_working": len(results),
            "minors": [
                {
                    "name": f"{r['First_Name']} {r['Last_Name']}",
                    "hours_worked": round(float(r["Actual_Hours"]), 1) if r["Actual_Hours"] else 0,
                    "has_break": r["Break_Start"] is not None,
                    "needs_break": (float(r["Actual_Hours"]) if r["Actual_Hours"] else 0) >= 3.5 and r["Break_Start"] is None
                }
                for r in results
            ]
        }

    return {"error": "Invalid query type"}


def _check_compliance(db, params: Dict) -> Dict:
    """Check compliance issues."""
    store_id = params["store_id"]
    check_type = params["check_type"]
    date = params["date"]

    if check_type == "violations" or check_type == "all":
        violations = db.query("""
            SELECT
                v.Violation_Type, v.Description, v.Penalty_Cost,
                e.First_Name, e.Last_Name, e.Is_Minor
            FROM Labor_Compliance_Violations v
            JOIN Employee_Master_Profile e ON v.Employee_ID = e.Employee_ID
            WHERE v.Store_ID = ? AND v.Violation_Date = ?
            ORDER BY v.Penalty_Cost DESC
        """, [store_id, date])

        if check_type == "violations":
            return {
                "date": date,
                "total_violations": len(violations),
                "total_penalty_cost": sum(float(v["Penalty_Cost"]) for v in violations),
                "violations": [
                    {
                        "employee": f"{v['First_Name']} {v['Last_Name']}",
                        "is_minor": v["Is_Minor"],
                        "type": v["Violation_Type"],
                        "description": v["Description"],
                        "penalty": float(v["Penalty_Cost"])
                    }
                    for v in violations
                ]
            }

    if check_type == "minor_status" or check_type == "all":
        minors = db.query("""
            SELECT
                e.First_Name, e.Last_Name,
                t.Actual_Hours, t.Break_Start, t.Clock_Out_Time
            FROM Time_Attendance_Actuals t
            JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
            WHERE t.Store_ID = ? AND t.Shift_Date = ? AND e.Is_Minor = true AND t.Is_No_Show = false
        """, [store_id, date])

        minor_issues = []
        for m in minors:
            hours = float(m["Actual_Hours"]) if m["Actual_Hours"] else 0
            needs_break = hours >= 3.5 and m["Break_Start"] is None
            if needs_break:
                minor_issues.append({
                    "name": f"{m['First_Name']} {m['Last_Name']}",
                    "hours_worked": round(hours, 1),
                    "issue": "Needs break immediately" if hours >= 4 else "Break due soon"
                })

        if check_type == "minor_status":
            return {
                "date": date,
                "minors_at_risk": len(minor_issues),
                "issues": minor_issues
            }

    if check_type == "overtime_risk" or check_type == "all":
        week_start = db.query_scalar(f"SELECT DATE_TRUNC('week', DATE '{date}')")
        overtime = db.query("""
            SELECT
                e.First_Name, e.Last_Name,
                SUM(t.Actual_Hours) as week_hours
            FROM Time_Attendance_Actuals t
            JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
            WHERE e.Store_ID = ? AND t.Shift_Date BETWEEN ? AND ?
            GROUP BY e.Employee_ID, e.First_Name, e.Last_Name
            HAVING SUM(t.Actual_Hours) >= 35
            ORDER BY SUM(t.Actual_Hours) DESC
        """, [store_id, str(week_start)[:10], date])

        if check_type == "overtime_risk":
            return {
                "date": date,
                "employees_at_risk": len(overtime),
                "overtime_risks": [
                    {
                        "name": f"{o['First_Name']} {o['Last_Name']}",
                        "week_hours": round(o["week_hours"], 1),
                        "hours_until_overtime": max(0, round(40 - o["week_hours"], 1))
                    }
                    for o in overtime
                ]
            }

    if check_type == "all":
        return {
            "date": date,
            "violations": {
                "count": len(violations),
                "total_penalty": sum(float(v["Penalty_Cost"]) for v in violations),
                "details": [{"employee": f"{v['First_Name']} {v['Last_Name']}", "type": v["Violation_Type"]} for v in violations]
            },
            "minor_issues": minor_issues,
            "overtime_risks": [{"name": f"{o['First_Name']} {o['Last_Name']}", "hours": round(o["week_hours"], 1)} for o in overtime]
        }

    return {"error": "Invalid check type"}


def _compare_performance(db, params: Dict) -> Dict:
    """Compare performance to historical periods."""
    store_id = params["store_id"]
    date = params["date"]
    comparison = params["comparison"]

    def get_stats(d):
        return db.query_one("""
            SELECT COUNT(*) as transactions, COALESCE(SUM(Total_Amount), 0) as revenue
            FROM Sales_Transactions_Header
            WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
        """, [store_id, d])

    current = get_stats(date)

    if comparison == "yesterday":
        compare_date = db.query_scalar(f"SELECT DATE '{date}' - INTERVAL 1 DAY")
    elif comparison == "last_week":
        compare_date = db.query_scalar(f"SELECT DATE '{date}' - INTERVAL 7 DAY")
    elif comparison == "same_day_last_week":
        compare_date = db.query_scalar(f"SELECT DATE '{date}' - INTERVAL 7 DAY")
    else:
        return {"error": "Invalid comparison type"}

    compare = get_stats(str(compare_date)[:10])

    def calc_change(curr, prev):
        if prev and prev > 0:
            return round((curr - prev) / prev * 100, 1)
        return 0

    return {
        "current_date": date,
        "compare_date": str(compare_date)[:10],
        "comparison_type": comparison,
        "current": {
            "transactions": current["transactions"],
            "revenue": round(current["revenue"], 2)
        },
        "comparison": {
            "transactions": compare["transactions"],
            "revenue": round(compare["revenue"], 2)
        },
        "change": {
            "transactions": calc_change(current["transactions"], compare["transactions"]),
            "revenue": calc_change(current["revenue"], compare["revenue"])
        }
    }


def _get_top_items(db, params: Dict) -> Dict:
    """Get top selling items."""
    store_id = params["store_id"]
    date = params["date"]
    limit = params.get("limit", 10)
    item_type = params.get("item_type", "all")

    type_filter = ""
    query_params = [store_id, date]
    if item_type and item_type != "all":
        type_filter = "AND li.Item_Type = ?"
        query_params.append(item_type)

    results = db.query(f"""
        SELECT
            li.Item_Name, li.Item_Type,
            COUNT(*) as quantity,
            SUM(li.Unit_Price * li.Quantity) as revenue
        FROM Sales_Order_Line_Items li
        JOIN Sales_Transactions_Header t ON li.Transaction_UUID = t.Transaction_UUID
        WHERE t.Store_ID = ? AND t.Business_Date = ? AND t.Is_Voided = false {type_filter}
        GROUP BY li.Item_Name, li.Item_Type
        ORDER BY quantity DESC
        LIMIT {limit}
    """, query_params)

    return {
        "date": date,
        "item_type_filter": item_type,
        "top_items": [
            {
                "rank": i + 1,
                "item": r["Item_Name"],
                "type": r["Item_Type"],
                "quantity": r["quantity"],
                "revenue": round(r["revenue"], 2)
            }
            for i, r in enumerate(results)
        ]
    }


def _analyze_linebuster(db, params: Dict) -> Dict:
    """Analyze linebuster effectiveness."""
    store_id = params["store_id"]
    date = params["date"]

    # Queue position by employee
    by_employee = db.query("""
        SELECT
            e.First_Name, e.Last_Name,
            AVG(t.Queue_Position) as avg_position,
            COUNT(*) as orders
        FROM Sales_Transactions_Header t
        JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
        WHERE t.Store_ID = ? AND t.Business_Date = ?
          AND t.Service_Channel = 'Drive_Thru'
          AND t.Queue_Position IS NOT NULL
        GROUP BY e.Employee_ID, e.First_Name, e.Last_Name
        HAVING COUNT(*) >= 10
        ORDER BY avg_position DESC
    """, [store_id, date])

    # Overall stats
    stats = db.query_one("""
        SELECT
            AVG(Queue_Position) as avg_position,
            COUNT(*) as total_drive_thru,
            SUM(CASE WHEN Queue_Position > 2 THEN 1 ELSE 0 END) as linebuster_orders
        FROM Sales_Transactions_Header
        WHERE Store_ID = ? AND Business_Date = ?
          AND Service_Channel = 'Drive_Thru'
          AND Queue_Position IS NOT NULL
    """, [store_id, date])

    return {
        "date": date,
        "total_drive_thru_orders": stats["total_drive_thru"],
        "linebuster_orders": stats["linebuster_orders"],
        "linebuster_percentage": round(stats["linebuster_orders"] / stats["total_drive_thru"] * 100, 1) if stats["total_drive_thru"] > 0 else 0,
        "avg_queue_position": round(stats["avg_position"], 1) if stats["avg_position"] else 0,
        "by_employee": [
            {
                "name": f"{r['First_Name']} {r['Last_Name']}",
                "avg_queue_position": round(r["avg_position"], 1),
                "orders": r["orders"]
            }
            for r in by_employee
        ],
        "top_linebuster": f"{by_employee[0]['First_Name']} {by_employee[0]['Last_Name']}" if by_employee else None
    }


def _get_peak_hours(db, params: Dict) -> Dict:
    """Get peak hour analysis."""
    store_id = params["store_id"]
    date = params["date"]

    results = db.query("""
        SELECT
            EXTRACT(hour FROM Open_Timestamp) as hour,
            COUNT(*) as transactions,
            SUM(Total_Amount) as revenue,
            AVG(Queue_Position) as avg_queue
        FROM Sales_Transactions_Header
        WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
        GROUP BY EXTRACT(hour FROM Open_Timestamp)
        ORDER BY transactions DESC
    """, [store_id, date])

    peak = results[0] if results else None

    return {
        "date": date,
        "peak_hour": f"{int(peak['hour']):02d}:00 - {int(peak['hour'])+1:02d}:00" if peak else None,
        "peak_transactions": peak["transactions"] if peak else 0,
        "peak_revenue": round(peak["revenue"], 2) if peak else 0,
        "hourly_breakdown": [
            {
                "hour": f"{int(r['hour']):02d}:00",
                "transactions": r["transactions"],
                "revenue": round(r["revenue"], 2),
                "is_peak": r == peak
            }
            for r in sorted(results, key=lambda x: x["hour"])
        ]
    }


def get_tools() -> List[Dict]:
    """Return the list of tool definitions."""
    return TOOL_DEFINITIONS
