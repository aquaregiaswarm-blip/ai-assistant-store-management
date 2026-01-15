"""Workforce and labor management endpoints."""
from fastapi import APIRouter, Query
from typing import Optional
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/workforce", tags=["workforce"])


@router.get("/schedule/today")
async def get_todays_schedule(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get today's scheduled shifts."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query("""
        SELECT
            s.Schedule_UUID,
            s.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Role_Code,
            e.Is_Minor,
            s.Shift_Start,
            s.Shift_End,
            s.Scheduled_Hours,
            s.Job_Role
        FROM Labor_Schedules_Published s
        JOIN Employee_Master_Profile e ON s.Employee_ID = e.Employee_ID
        WHERE s.Store_ID = ? AND s.Shift_Date = ?
        ORDER BY s.Shift_Start
    """, [store_id, target_date])

    return [
        {
            "schedule_id": r["Schedule_UUID"],
            "employee_id": r["Employee_ID"],
            "employee_name": f"{r['First_Name']} {r['Last_Name']}",
            "role": r["Role_Code"],
            "job_role": r["Job_Role"],
            "is_minor": r["Is_Minor"],
            "shift_start": str(r["Shift_Start"]),
            "shift_end": str(r["Shift_End"]),
            "scheduled_hours": float(r["Scheduled_Hours"])
        }
        for r in results
    ]


@router.get("/whos-working")
async def get_whos_working(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get employees currently clocked in."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query("""
        SELECT
            t.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Role_Code,
            e.Is_Minor,
            e.Hourly_Wage,
            t.Clock_In_Time,
            t.Clock_Out_Time,
            t.Break_Start,
            t.Break_End,
            t.Actual_Hours,
            t.Is_Late,
            t.Late_Minutes
        FROM Time_Attendance_Actuals t
        JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
        WHERE t.Store_ID = ? AND t.Shift_Date = ? AND t.Is_No_Show = false
        ORDER BY t.Clock_In_Time
    """, [store_id, target_date])

    return [
        {
            "employee_id": r["Employee_ID"],
            "name": f"{r['First_Name']} {r['Last_Name']}",
            "first_name": r["First_Name"],
            "last_name": r["Last_Name"],
            "role": r["Role_Code"],
            "is_minor": r["Is_Minor"],
            "hourly_wage": float(r["Hourly_Wage"]),
            "clock_in": str(r["Clock_In_Time"]) if r["Clock_In_Time"] else None,
            "clock_out": str(r["Clock_Out_Time"]) if r["Clock_Out_Time"] else None,
            "break_start": str(r["Break_Start"]) if r["Break_Start"] else None,
            "break_end": str(r["Break_End"]) if r["Break_End"] else None,
            "hours_worked": float(r["Actual_Hours"]) if r["Actual_Hours"] else 0,
            "is_late": r["Is_Late"],
            "late_minutes": r["Late_Minutes"],
            "still_working": r["Clock_Out_Time"] is None
        }
        for r in results
    ]


@router.get("/compliance/violations")
async def get_compliance_violations(
    store_id: int = Query(1001),
    date: str = Query(None),
    days_back: int = Query(7, description="Number of days to look back")
):
    """Get recent compliance violations."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query("""
        SELECT
            v.Violation_UUID,
            v.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Is_Minor,
            v.Violation_Date,
            v.Violation_Type,
            v.Description,
            v.Penalty_Cost,
            v.Manager_Ack,
            v.Resolved
        FROM Labor_Compliance_Violations v
        JOIN Employee_Master_Profile e ON v.Employee_ID = e.Employee_ID
        WHERE v.Store_ID = ?
          AND v.Violation_Date BETWEEN DATE ? - INTERVAL ? DAY AND DATE ?
        ORDER BY v.Violation_Date DESC, v.Penalty_Cost DESC
    """, [store_id, target_date, days_back, target_date])

    return [
        {
            "violation_id": r["Violation_UUID"],
            "employee_id": r["Employee_ID"],
            "employee_name": f"{r['First_Name']} {r['Last_Name']}",
            "is_minor": r["Is_Minor"],
            "date": str(r["Violation_Date"]),
            "type": r["Violation_Type"],
            "description": r["Description"],
            "penalty_cost": float(r["Penalty_Cost"]),
            "acknowledged": r["Manager_Ack"],
            "resolved": r["Resolved"]
        }
        for r in results
    ]


@router.get("/compliance/minors")
async def get_minor_status(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get status of all minor employees working today."""
    db = get_db()
    target_date = date or settings.data_current_date

    results = db.query("""
        SELECT
            e.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Date_of_Birth,
            t.Clock_In_Time,
            t.Clock_Out_Time,
            t.Break_Start,
            t.Break_End,
            t.Actual_Hours,
            s.Shift_End
        FROM Employee_Master_Profile e
        JOIN Time_Attendance_Actuals t ON e.Employee_ID = t.Employee_ID
        LEFT JOIN Labor_Schedules_Published s ON t.Schedule_UUID = s.Schedule_UUID
        WHERE e.Store_ID = ?
          AND e.Is_Minor = true
          AND t.Shift_Date = ?
          AND t.Is_No_Show = false
    """, [store_id, target_date])

    minors = []
    for r in results:
        hours_worked = float(r["Actual_Hours"]) if r["Actual_Hours"] else 0
        has_break = r["Break_Start"] is not None
        needs_break = hours_worked >= 3.5 and not has_break

        minors.append({
            "employee_id": r["Employee_ID"],
            "name": f"{r['First_Name']} {r['Last_Name']}",
            "clock_in": str(r["Clock_In_Time"]) if r["Clock_In_Time"] else None,
            "scheduled_end": str(r["Shift_End"]) if r["Shift_End"] else None,
            "hours_worked": hours_worked,
            "has_taken_break": has_break,
            "needs_break_soon": needs_break,
            "break_urgency": "high" if hours_worked >= 4 and not has_break else "medium" if needs_break else "none"
        })

    return minors


@router.get("/overtime-risk")
async def get_overtime_risk(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get employees approaching overtime this week."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Get week start (Monday)
    week_start = db.query_scalar(f"""
        SELECT DATE_TRUNC('week', DATE '{target_date}')
    """)

    results = db.query("""
        SELECT
            e.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Role_Code,
            e.Hourly_Wage,
            SUM(t.Actual_Hours) as week_hours
        FROM Employee_Master_Profile e
        JOIN Time_Attendance_Actuals t ON e.Employee_ID = t.Employee_ID
        WHERE e.Store_ID = ?
          AND t.Shift_Date BETWEEN ? AND ?
        GROUP BY e.Employee_ID, e.First_Name, e.Last_Name, e.Role_Code, e.Hourly_Wage
        HAVING SUM(t.Actual_Hours) >= 30
        ORDER BY SUM(t.Actual_Hours) DESC
    """, [store_id, str(week_start)[:10], target_date])

    return [
        {
            "employee_id": r["Employee_ID"],
            "name": f"{r['First_Name']} {r['Last_Name']}",
            "role": r["Role_Code"],
            "week_hours": round(r["week_hours"], 1),
            "hours_until_overtime": max(0, 40 - r["week_hours"]),
            "overtime_risk": "high" if r["week_hours"] >= 38 else "medium" if r["week_hours"] >= 35 else "low",
            "projected_overtime_cost": round(max(0, r["week_hours"] - 40) * r["Hourly_Wage"] * 1.5, 2)
        }
        for r in results
    ]


@router.get("/attendance")
async def get_attendance_issues(
    store_id: int = Query(1001),
    date: str = Query(None)
):
    """Get attendance issues (late arrivals, no-shows)."""
    db = get_db()
    target_date = date or settings.data_current_date

    # Late arrivals
    late = db.query("""
        SELECT
            t.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Role_Code,
            t.Late_Minutes,
            t.Clock_In_Time,
            s.Shift_Start
        FROM Time_Attendance_Actuals t
        JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
        LEFT JOIN Labor_Schedules_Published s ON t.Schedule_UUID = s.Schedule_UUID
        WHERE t.Store_ID = ? AND t.Shift_Date = ? AND t.Is_Late = true
        ORDER BY t.Late_Minutes DESC
    """, [store_id, target_date])

    # No-shows
    no_shows = db.query("""
        SELECT
            t.Employee_ID,
            e.First_Name,
            e.Last_Name,
            e.Role_Code,
            s.Shift_Start,
            s.Shift_End
        FROM Time_Attendance_Actuals t
        JOIN Employee_Master_Profile e ON t.Employee_ID = e.Employee_ID
        LEFT JOIN Labor_Schedules_Published s ON t.Schedule_UUID = s.Schedule_UUID
        WHERE t.Store_ID = ? AND t.Shift_Date = ? AND t.Is_No_Show = true
    """, [store_id, target_date])

    return {
        "late_arrivals": [
            {
                "employee_id": r["Employee_ID"],
                "name": f"{r['First_Name']} {r['Last_Name']}",
                "role": r["Role_Code"],
                "late_minutes": r["Late_Minutes"],
                "scheduled_start": str(r["Shift_Start"]) if r["Shift_Start"] else None,
                "actual_arrival": str(r["Clock_In_Time"]) if r["Clock_In_Time"] else None
            }
            for r in late
        ],
        "no_shows": [
            {
                "employee_id": r["Employee_ID"],
                "name": f"{r['First_Name']} {r['Last_Name']}",
                "role": r["Role_Code"],
                "scheduled_start": str(r["Shift_Start"]) if r["Shift_Start"] else None,
                "scheduled_end": str(r["Shift_End"]) if r["Shift_End"] else None
            }
            for r in no_shows
        ],
        "summary": {
            "total_late": len(late),
            "total_no_shows": len(no_shows),
            "avg_late_minutes": round(sum(r["Late_Minutes"] for r in late) / len(late), 1) if late else 0
        }
    }
