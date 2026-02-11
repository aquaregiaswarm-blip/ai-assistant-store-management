# GCP Deployment Plan — Swig GM Dashboard (with BigQuery)
 
## Executive Summary
 
This plan deploys the Swig GM Dashboard to Google Cloud Platform, **replacing DuckDB with BigQuery** as the data store. The architecture uses **Cloud Run** (scales to zero) with a single container serving both the React frontend and FastAPI backend. BigQuery provides a managed, serverless analytics database that aligns with the GCP ecosystem.
 
**Estimated monthly cost**: $0 idle, ~$2-5 with light demo usage (both BigQuery and Cloud Run have generous free tiers).
 
---
 
## Table of Contents
 
1. [Architecture Overview](#1-architecture-overview)
2. [Cost Estimate](#2-cost-estimate)
3. [Prerequisites](#3-prerequisites)
4. [Phase 1: BigQuery Setup & Data Loading](#phase-1-bigquery-setup--data-loading)
5. [Phase 2: Backend Refactoring (DuckDB → BigQuery)](#phase-2-backend-refactoring-duckdb--bigquery)
6. [Phase 3: Containerize the Application](#phase-3-containerize-the-application)
7. [Phase 4: GCP Project Setup](#phase-4-gcp-project-setup)
8. [Phase 5: Deploy to Cloud Run](#phase-5-deploy-to-cloud-run)
9. [Phase 6: CI/CD (Optional)](#phase-6-cicd-optional)
10. [Security Considerations](#security-considerations)
11. [SQL Migration Reference](#sql-migration-reference)
12. [Complete File Change Manifest](#complete-file-change-manifest)
13. [Deployment Checklist](#deployment-checklist)
 
---
 
## 1. Architecture Overview
 
```
                    ┌──────────────────────────────┐
                    │         Cloud Run             │
                    │    (scales 0 → N instances)   │
                    │                               │
   User ──HTTPS──► │  FastAPI (uvicorn)             │
                    │  ├── /api/*  → API routes      │
                    │  └── /*     → Static React     │
                    │               (dist/ files)    │
                    └──────────┬──────┬─────────────┘
                               │      │
                       ┌───────┘      └───────┐
                       ▼                      ▼
            ┌──────────────────┐   ┌──────────────────────┐
            │   BigQuery       │   │   OpenAI API         │
            │   (serverless)   │   │   (external, HTTPS)  │
            │                  │   └──────────────────────┘
            │  Dataset:        │
            │  swig_operations │
            │  (20 tables)     │
            └──────────────────┘
 
   Secrets:
   ┌──────────────────────────┐
   │  GCP Secret Manager      │
   │  └── OPENAI_API_KEY      │
   └──────────────────────────┘
```
 
### Key Design Decisions
 
| Decision | Rationale |
|----------|-----------|
| **BigQuery over DuckDB** | Fully managed, serverless, generous free tier, native GCP integration |
| **Single Cloud Run container** | FastAPI serves both API + static React files. No CORS issues, minimal cost |
| **Named query parameters** | BigQuery uses `@param` syntax vs DuckDB's `?` — all queries must be rewritten |
| **Workload Identity** | Cloud Run service account accesses BigQuery directly — no key files needed |
| **Secret Manager** | OpenAI API key stored securely, injected at runtime |
 
### DuckDB vs BigQuery Trade-offs
 
| Factor | DuckDB (current) | BigQuery (proposed) |
|--------|------------------|---------------------|
| Query latency | ~1-5ms (in-process) | ~500ms-2s (network) |
| Cost | $0 (embedded file) | $0 (free tier: 10GB storage, 1TB queries/month) |
| Code changes | None | Rewrite database layer + all SQL queries |
| Cold start impact | None | None (BQ is always-on serverless) |
| Data updates | Rebuild container | SQL INSERT/UPDATE directly |
| Scalability | Single container only | Unlimited concurrent readers |
| GCP integration | None | Native (Looker, Data Studio, etc.) |
| Local development | Works offline | Requires GCP credentials + network |
 
---
 
## 2. Cost Estimate
 
### Monthly Cost — Light Demo Usage (~100 sessions/month)
 
| Service | Free Tier | Estimated Usage | Cost |
|---------|-----------|-----------------|------|
| Cloud Run | 2M requests, 360K vCPU-sec | ~5K requests | **$0** |
| BigQuery Storage | 10 GB/month | ~50 MB (20 tables, 335K rows) | **$0** |
| BigQuery Queries | 1 TB/month | ~1-5 GB | **$0** |
| Artifact Registry | 0.5 GB free | ~500 MB image | **$0** |
| Secret Manager | 6 versions free | 1 secret | **$0** |
| OpenAI API (external) | N/A | ~100 GPT-4o calls | **~$1-5** |
| **Total** | | | **~$1-5/month** |
 
### When Idle: **$0/month** (Cloud Run scales to zero, BigQuery charges nothing for idle data under 10GB)
 
---
 
## 3. Prerequisites
 
- [ ] GCP account with billing enabled (free tier sufficient)
- [ ] `gcloud` CLI installed and authenticated
- [ ] Docker installed locally
- [ ] Node.js 18+ and Python 3.11+
- [ ] OpenAI API key
- [ ] DuckDB database file generated (for data export to BigQuery)
 
---
 
## Phase 1: BigQuery Setup & Data Loading
 
### 1.1 Create the BigQuery Dataset
 
```bash
export GCP_PROJECT_ID="swig-gm-dashboard"
export BQ_DATASET="swig_operations"
export GCP_REGION="us-central1"
 
# Create the dataset
bq mk --dataset \
    --location=US \
    --description="Swig GM Dashboard operational data" \
    ${GCP_PROJECT_ID}:${BQ_DATASET}
```
 
### 1.2 Create BigQuery Table Schema
 
Create file `swig-gm-dashboard/bigquery/create_tables.sql`. This translates the DuckDB schema to BigQuery DDL:
 
```sql
-- =============================================================================
-- BigQuery Schema for Swig Operations
-- Run each CREATE TABLE statement in the BigQuery console or via bq CLI
-- =============================================================================
 
-- 1. Organization_Stores
CREATE TABLE IF NOT EXISTS `swig_operations.Organization_Stores` (
    Store_ID INT64 NOT NULL,
    Store_Name STRING NOT NULL,
    Address STRING,
    City STRING,
    State STRING,
    Zip STRING,
    Latitude FLOAT64,
    Longitude FLOAT64,
    Timezone STRING DEFAULT 'America/Denver',
    Open_Time TIME,
    Close_Time TIME,
    Is_Active BOOL DEFAULT TRUE,
    Open_Date DATE
);
 
-- 2. Product_Categories
CREATE TABLE IF NOT EXISTS `swig_operations.Product_Categories` (
    Category_ID INT64 NOT NULL,
    Category_Name STRING NOT NULL,
    Display_Order INT64
);
 
-- 3. Product_Catalog
CREATE TABLE IF NOT EXISTS `swig_operations.Product_Catalog` (
    Item_SKU STRING NOT NULL,
    Item_Name STRING NOT NULL,
    Category_ID INT64,
    Item_Type STRING,  -- 'Base_Beverage', 'Modifier', 'Food', 'Merch'
    Base_Price FLOAT64 NOT NULL,
    Is_Available BOOL DEFAULT TRUE,
    Calories INT64,
    Size_Oz INT64,
    Is_Sugar_Free BOOL DEFAULT FALSE,
    Description STRING
);
 
-- 4. Vendors
CREATE TABLE IF NOT EXISTS `swig_operations.Vendors` (
    Vendor_ID INT64 NOT NULL,
    Vendor_Name STRING NOT NULL,
    Contact_Name STRING,
    Contact_Email STRING,
    Contact_Phone STRING,
    Lead_Time_Days INT64 DEFAULT 3,
    Is_Active BOOL DEFAULT TRUE
);
 
-- 5. Job_Roles
CREATE TABLE IF NOT EXISTS `swig_operations.Job_Roles` (
    Role_Code STRING NOT NULL,
    Role_Name STRING NOT NULL,
    Base_Hourly_Rate FLOAT64,
    Can_Manage BOOL DEFAULT FALSE,
    Can_Handle_Cash BOOL DEFAULT TRUE,
    Min_Age INT64 DEFAULT 16
);
 
-- 6. Loyalty_Profiles
CREATE TABLE IF NOT EXISTS `swig_operations.Loyalty_Profiles` (
    Customer_Loyalty_ID STRING NOT NULL,
    First_Name STRING,
    Phone_Last4 STRING,
    Email_Domain STRING,
    Join_Date DATE,
    Points_Balance INT64 DEFAULT 0,
    Lifetime_Spend FLOAT64 DEFAULT 0,
    Visit_Count INT64 DEFAULT 0,
    Preferred_Store_ID INT64,
    Last_Visit_Date DATE
);
 
-- 7. Sales_Transactions_Header
CREATE TABLE IF NOT EXISTS `swig_operations.Sales_Transactions_Header` (
    Transaction_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Business_Date DATE NOT NULL,
    Open_Timestamp TIMESTAMP NOT NULL,
    Close_Timestamp TIMESTAMP,
    Service_Channel STRING,
    Order_Source_Device STRING,
    Employee_ID INT64,
    Customer_Loyalty_ID STRING,
    Queue_Position INT64,
    Vehicle_Descriptor STRING,
    Subtotal_Amount FLOAT64,
    Tax_Amount FLOAT64,
    Discount_Total FLOAT64 DEFAULT 0,
    Total_Amount FLOAT64,
    Is_Voided BOOL DEFAULT FALSE
)
PARTITION BY Business_Date
CLUSTER BY Store_ID;
 
-- 8. Sales_Order_Line_Items
CREATE TABLE IF NOT EXISTS `swig_operations.Sales_Order_Line_Items` (
    Line_Item_UUID STRING NOT NULL,
    Transaction_UUID STRING NOT NULL,
    Item_SKU STRING,
    Item_Name STRING,
    Item_Type STRING,
    Quantity INT64 DEFAULT 1,
    Unit_Price FLOAT64,
    Line_Total FLOAT64,
    Parent_Line_UUID STRING,
    Modifier_Group STRING,
    Price_Override FLOAT64,
    Is_Comped BOOL DEFAULT FALSE
);
 
-- 9. Sales_Payments
CREATE TABLE IF NOT EXISTS `swig_operations.Sales_Payments` (
    Payment_UUID STRING NOT NULL,
    Transaction_UUID STRING NOT NULL,
    Tender_Type STRING,
    Amount_Tendered FLOAT64 NOT NULL,
    Tip_Amount FLOAT64 DEFAULT 0,
    Change_Given FLOAT64 DEFAULT 0,
    Auth_Code STRING,
    Masked_PAN STRING,
    Payment_Timestamp TIMESTAMP,
    Is_Refund BOOL DEFAULT FALSE
);
 
-- 10. Drive_Thru_Loop_Metrics
CREATE TABLE IF NOT EXISTS `swig_operations.Drive_Thru_Loop_Metrics` (
    Loop_Event_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Transaction_UUID STRING,
    Sensor_ID STRING,
    Arrival_Time TIMESTAMP NOT NULL,
    Departure_Time TIMESTAMP,
    Duration_Seconds INT64,
    Car_Count_Hour INT64,
    Business_Date DATE
)
PARTITION BY Business_Date
CLUSTER BY Store_ID;
 
-- 11. Employee_Master_Profile
CREATE TABLE IF NOT EXISTS `swig_operations.Employee_Master_Profile` (
    Employee_ID INT64 NOT NULL,
    Store_ID INT64 NOT NULL,
    Harri_UID STRING,
    First_Name STRING NOT NULL,
    Last_Name STRING NOT NULL,
    Role_Code STRING,
    Hire_Date DATE NOT NULL,
    Date_of_Birth DATE,
    Is_Minor BOOL DEFAULT FALSE,
    Hourly_Wage FLOAT64,
    Email STRING,
    Phone STRING,
    Food_Handler_Exp DATE,
    Status STRING DEFAULT 'Active'
);
 
-- 12. Labor_Schedules_Published
CREATE TABLE IF NOT EXISTS `swig_operations.Labor_Schedules_Published` (
    Schedule_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Employee_ID INT64 NOT NULL,
    Shift_Date DATE NOT NULL,
    Shift_Start TIMESTAMP NOT NULL,
    Shift_End TIMESTAMP NOT NULL,
    Scheduled_Hours FLOAT64,
    Job_Role STRING,
    Is_Posted BOOL DEFAULT TRUE,
    Forecast_Sales FLOAT64,
    Created_At TIMESTAMP
)
PARTITION BY Shift_Date
CLUSTER BY Store_ID;
 
-- 13. Time_Attendance_Actuals
CREATE TABLE IF NOT EXISTS `swig_operations.Time_Attendance_Actuals` (
    Punch_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Employee_ID INT64 NOT NULL,
    Schedule_UUID STRING,
    Shift_Date DATE NOT NULL,
    Clock_In_Time TIMESTAMP,
    Clock_Out_Time TIMESTAMP,
    Break_Start TIMESTAMP,
    Break_End TIMESTAMP,
    Break_Duration_Minutes INT64,
    Actual_Hours FLOAT64,
    Validation_Method STRING,
    Is_Late BOOL DEFAULT FALSE,
    Late_Minutes INT64 DEFAULT 0,
    Is_No_Show BOOL DEFAULT FALSE
)
PARTITION BY Shift_Date
CLUSTER BY Store_ID;
 
-- 14. Labor_Compliance_Violations
CREATE TABLE IF NOT EXISTS `swig_operations.Labor_Compliance_Violations` (
    Violation_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Employee_ID INT64 NOT NULL,
    Punch_UUID STRING,
    Violation_Date DATE NOT NULL,
    Violation_Type STRING,
    Description STRING,
    Penalty_Cost FLOAT64 DEFAULT 0,
    Manager_Ack BOOL DEFAULT FALSE,
    Resolved BOOL DEFAULT FALSE
)
PARTITION BY Violation_Date
CLUSTER BY Store_ID;
 
-- 15. Inventory_Item_Master
CREATE TABLE IF NOT EXISTS `swig_operations.Inventory_Item_Master` (
    Inventory_ID INT64 NOT NULL,
    Description STRING NOT NULL,
    Category STRING,
    Vendor_ID INT64,
    Count_UOM STRING,
    Recipe_UOM STRING,
    Conversion_Factor FLOAT64,
    Unit_Cost FLOAT64,
    Par_Level FLOAT64,
    Reorder_Point FLOAT64,
    Is_Active BOOL DEFAULT TRUE
);
 
-- 16. Recipe_BOM_Mapping
CREATE TABLE IF NOT EXISTS `swig_operations.Recipe_BOM_Mapping` (
    Recipe_ID INT64 NOT NULL,
    Sales_Item_SKU STRING NOT NULL,
    Inventory_ID INT64 NOT NULL,
    Quantity_Required FLOAT64 NOT NULL,
    Recipe_UOM STRING,
    Yield_Loss_Pct FLOAT64 DEFAULT 0,
    Is_Optional BOOL DEFAULT FALSE
);
 
-- 17. Inventory_Transactions_Ledger
CREATE TABLE IF NOT EXISTS `swig_operations.Inventory_Transactions_Ledger` (
    Trans_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Inventory_ID INT64 NOT NULL,
    Transaction_Date DATE NOT NULL,
    Transaction_Time TIMESTAMP NOT NULL,
    Transaction_Type STRING,
    Quantity_Change FLOAT64,
    Running_Balance FLOAT64,
    Cost_Value FLOAT64,
    Reason_Code STRING,
    Reference_ID STRING,
    Employee_ID INT64
)
PARTITION BY Transaction_Date
CLUSTER BY Store_ID;
 
-- 18. Daily_Cash_Reconciliation
CREATE TABLE IF NOT EXISTS `swig_operations.Daily_Cash_Reconciliation` (
    Reconciliation_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Business_Date DATE NOT NULL,
    Shift STRING,
    Expected_Cash FLOAT64,
    Actual_Cash FLOAT64,
    Variance FLOAT64,
    Variance_Pct FLOAT64,
    Counted_By_Employee_ID INT64,
    Verified_By_Employee_ID INT64,
    Count_Timestamp TIMESTAMP,
    Notes STRING
);
 
-- 19. Discounts_Promotions
CREATE TABLE IF NOT EXISTS `swig_operations.Discounts_Promotions` (
    Promo_ID INT64 NOT NULL,
    Promo_Code STRING,
    Promo_Name STRING,
    Promo_Type STRING,
    Discount_Value FLOAT64,
    Min_Purchase FLOAT64 DEFAULT 0,
    Applicable_Items STRING,
    Start_Date DATE,
    End_Date DATE,
    Is_Active BOOL DEFAULT TRUE,
    Usage_Count INT64 DEFAULT 0
);
 
-- 20. Equipment_Status
CREATE TABLE IF NOT EXISTS `swig_operations.Equipment_Status` (
    Status_UUID STRING NOT NULL,
    Store_ID INT64 NOT NULL,
    Equipment_ID STRING,
    Equipment_Type STRING,
    Equipment_Name STRING,
    Status STRING,
    Status_Change_Time TIMESTAMP NOT NULL,
    Expected_Resolution TIMESTAMP,
    Impact_Level STRING,
    Notes STRING,
    Reported_By_Employee_ID INT64
);
```
 
**Key BigQuery schema differences from DuckDB:**
- `INTEGER` → `INT64`
- `VARCHAR(n)` → `STRING`
- `DECIMAL(p,s)` → `FLOAT64` (or `NUMERIC` for exact precision)
- `BOOLEAN` → `BOOL`
- No `CHECK` constraints (enforced at application level)
- No foreign key enforcement (BigQuery doesn't enforce FK constraints)
- Added `PARTITION BY` on date columns for the large fact tables (free performance/cost optimization)
- Added `CLUSTER BY Store_ID` on partitioned tables
 
### 1.3 Export DuckDB Data and Load into BigQuery
 
Create `swig-gm-dashboard/bigquery/load_data.py`:
 
```python
"""Export data from DuckDB and load into BigQuery."""
import duckdb
import json
import subprocess
import tempfile
import os
from pathlib import Path
 
# Configuration
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "../../swig_operations.duckdb")
GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "swig-gm-dashboard")
BQ_DATASET = "swig_operations"
 
# All tables to export
TABLES = [
    "Organization_Stores",
    "Product_Categories",
    "Product_Catalog",
    "Vendors",
    "Job_Roles",
    "Loyalty_Profiles",
    "Sales_Transactions_Header",
    "Sales_Order_Line_Items",
    "Sales_Payments",
    "Drive_Thru_Loop_Metrics",
    "Employee_Master_Profile",
    "Labor_Schedules_Published",
    "Time_Attendance_Actuals",
    "Labor_Compliance_Violations",
    "Inventory_Item_Master",
    "Recipe_BOM_Mapping",
    "Inventory_Transactions_Ledger",
    "Daily_Cash_Reconciliation",
    "Discounts_Promotions",
    "Equipment_Status",
]
 
 
def export_and_load():
    """Export each DuckDB table to JSONL and load into BigQuery."""
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
 
    for table in TABLES:
        print(f"\n--- {table} ---")
 
        # Export to temporary JSONL file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as f:
            tmpfile = f.name
 
            # Get rows as dicts
            result = conn.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
 
            print(f"  Exporting {len(rows)} rows...")
 
            for row in rows:
                record = {}
                for col, val in zip(columns, row):
                    if val is None:
                        record[col] = None
                    elif hasattr(val, "isoformat"):
                        record[col] = val.isoformat()
                    elif isinstance(val, (int, float, bool, str)):
                        record[col] = val
                    else:
                        record[col] = str(val)
                f.write(json.dumps(record) + "\n")
 
        # Load into BigQuery using bq CLI
        destination = f"{GCP_PROJECT}:{BQ_DATASET}.{table}"
        print(f"  Loading into {destination}...")
 
        cmd = [
            "bq", "load",
            "--source_format=NEWLINE_DELIMITED_JSON",
            "--replace",
            "--autodetect",
            destination,
            tmpfile,
        ]
 
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr}")
        else:
            print(f"  OK")
 
        os.unlink(tmpfile)
 
    conn.close()
    print("\nDone! All tables loaded into BigQuery.")
 
 
if __name__ == "__main__":
    export_and_load()
```
 
**Usage:**
 
```bash
cd swig-gm-dashboard/bigquery/
 
# Make sure gcloud is authenticated and project is set
gcloud config set project swig-gm-dashboard
 
# Run the data loader (DuckDB file must exist)
python load_data.py
```
 
### 1.4 Verify Data in BigQuery
 
```bash
# Check row counts
bq query --use_legacy_sql=false \
    "SELECT 'Sales_Transactions_Header' as tbl, COUNT(*) as rows FROM swig_operations.Sales_Transactions_Header
     UNION ALL
     SELECT 'Employee_Master_Profile', COUNT(*) FROM swig_operations.Employee_Master_Profile
     UNION ALL
     SELECT 'Sales_Order_Line_Items', COUNT(*) FROM swig_operations.Sales_Order_Line_Items"
```
 
---
 
## Phase 2: Backend Refactoring (DuckDB → BigQuery)
 
This is the largest phase. Every file that uses DuckDB must be rewritten to use the BigQuery Python client.
 
### Key SQL Dialect Differences
 
| Feature | DuckDB | BigQuery |
|---------|--------|----------|
| **Parameters** | Positional `?` | Named `@param_name` |
| **Date arithmetic** | `DATE '2025-01-26' - INTERVAL 1 DAY` | `DATE_SUB(DATE '2025-01-26', INTERVAL 1 DAY)` |
| **Date truncation** | `DATE_TRUNC('week', date_col)` | `DATE_TRUNC(date_col, WEEK(MONDAY))` |
| **Extract hour** | `EXTRACT(hour FROM ts)` | `EXTRACT(HOUR FROM ts)` |
| **Boolean literals** | `true` / `false` | `TRUE` / `FALSE` |
| **Limit** | `LIMIT N` (variable) | `LIMIT` (literal only — can't parameterize) |
| **Null-safe divide** | `NULLIF(x, 0)` | `NULLIF(x, 0)` or `SAFE_DIVIDE(a, b)` |
| **String concat** | `\|\|` | `CONCAT()` or `\|\|` |
| **Table references** | `table_name` | `` `project.dataset.table` `` or `dataset.table` |
 
### 2.1 Update `requirements.txt`
 
**File:** `backend/requirements.txt`
 
```
fastapi>=0.109.0
uvicorn>=0.27.0
google-cloud-bigquery>=3.0.0
openai>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
httpx>=0.26.0
```
 
**Changes:** Replaced `duckdb>=0.9.0` with `google-cloud-bigquery>=3.0.0`
 
### 2.2 Update `config.py`
 
**File:** `backend/app/config.py`
 
```python
"""Configuration settings for the Swig GM Dashboard API."""
import os
from pydantic_settings import BaseSettings
 
 
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
 
    # BigQuery
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "swig-gm-dashboard")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "swig_operations")
 
    # OpenAI API Key
    openai_api_key: str = ""
 
    # AWS Bedrock settings (fallback if no OpenAI key)
    aws_region: str = "us-west-2"
 
    # API Settings
    api_prefix: str = "/api"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
 
    # The "current" date in the synthetic data (last day of generated data)
    data_current_date: str = "2025-01-26"
 
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
 
 
settings = Settings()
```
 
**Changes:**
- Removed `duckdb_path`
- Added `gcp_project_id` and `bigquery_dataset`
- Defaulted `debug` to `false`
 
### 2.3 Rewrite `database.py` (Core Change)
 
**File:** `backend/app/database.py`
 
This is the central abstraction. The BigQuery client replaces the DuckDB connection. The `query()` / `query_one()` / `query_scalar()` interface stays the same so router code changes are minimized.
 
```python
"""BigQuery database connection and query utilities."""
from google.cloud import bigquery
from typing import Any, Dict, List, Optional
from .config import settings
 
 
class Database:
    """BigQuery connection manager.
 
    Provides the same query()/query_one()/query_scalar() interface
    as the original DuckDB implementation so that router code changes
    are limited to SQL dialect differences.
    """
 
    _instance: Optional["Database"] = None
    _client: Optional[bigquery.Client] = None
 
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
 
    @property
    def dataset(self) -> str:
        """Fully-qualified dataset reference."""
        return f"{settings.gcp_project_id}.{settings.bigquery_dataset}"
 
    def connect(self) -> bigquery.Client:
        """Get or create BigQuery client."""
        if self._client is None:
            self._client = bigquery.Client(project=settings.gcp_project_id)
        return self._client
 
    def _build_job_config(
        self, params: Optional[Dict[str, Any]]
    ) -> Optional[bigquery.QueryJobConfig]:
        """Build a QueryJobConfig with typed parameters."""
        if not params:
            return None
 
        query_params = []
        for name, value in params.items():
            if isinstance(value, bool):
                query_params.append(
                    bigquery.ScalarQueryParameter(name, "BOOL", value)
                )
            elif isinstance(value, int):
                query_params.append(
                    bigquery.ScalarQueryParameter(name, "INT64", value)
                )
            elif isinstance(value, float):
                query_params.append(
                    bigquery.ScalarQueryParameter(name, "FLOAT64", value)
                )
            elif isinstance(value, str):
                query_params.append(
                    bigquery.ScalarQueryParameter(name, "STRING", value)
                )
            else:
                query_params.append(
                    bigquery.ScalarQueryParameter(name, "STRING", str(value))
                )
 
        config = bigquery.QueryJobConfig(query_parameters=query_params)
        return config
 
    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Execute a query and return results as list of dicts.
 
        Args:
            sql: SQL query string using @param_name for parameters.
            params: Dict of parameter name -> value. Example:
                    {"store_id": 1001, "target_date": "2025-01-26"}
        """
        client = self.connect()
        job_config = self._build_job_config(params)
        result = client.query(sql, job_config=job_config).result()
        return [dict(row) for row in result]
 
    def query_one(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict]:
        """Execute a query and return a single result."""
        results = self.query(sql, params)
        return results[0] if results else None
 
    def query_scalar(
        self, sql: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a query and return a single scalar value."""
        client = self.connect()
        job_config = self._build_job_config(params)
        result = client.query(sql, job_config=job_config).result()
        row = next(iter(result), None)
        if row is None:
            return None
        values = list(row.values())
        return values[0] if values else None
 
 
# Global database instance
db = Database()
 
 
def get_db() -> Database:
    """Dependency injection for database."""
    return db
```
 
**Critical API change:** The `params` argument changes from a **positional list** `[store_id, date]` to a **named dict** `{"store_id": store_id, "target_date": date}`. This means every call site must be updated.
 
### 2.4 Rewrite `routers/dashboard.py` (Detailed Example)
 
**File:** `backend/app/routers/dashboard.py`
 
```python
"""Dashboard KPI endpoints."""
from fastapi import APIRouter, Query
from typing import List, Optional
from ..database import get_db
from ..config import settings
 
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
 
# Helper: dataset prefix for table references
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
 
    tx_stats = db.query_one(f"""
        SELECT
            COUNT(*) as transaction_count,
            COALESCE(SUM(Total_Amount), 0) as total_revenue,
            COALESCE(AVG(Total_Amount), 0) as avg_ticket,
            COUNT(DISTINCT Employee_ID) as employees_sold
        FROM `{DS}.Sales_Transactions_Header`
        WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
    """, {"store_id": store_id, "target_date": target_date})
 
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
 
    labor = db.query_one(f"""
        SELECT
            COALESCE(SUM(t.Actual_Hours * e.Hourly_Wage), 0) as labor_cost
        FROM `{DS}.Time_Attendance_Actuals` t
        JOIN `{DS}.Employee_Master_Profile` e ON t.Employee_ID = e.Employee_ID
        WHERE t.Store_ID = @store_id AND t.Shift_Date = @target_date
    """, {"store_id": store_id, "target_date": target_date})
 
    # ... (rest of KPI logic stays exactly the same — calculate comparisons in Python)
```
 
### 2.5 Pattern for All Other Routers
 
Every router follows the same transformation pattern:
 
```python
# BEFORE (DuckDB): positional ? params, bare table names
result = db.query("""
    SELECT * FROM Sales_Transactions_Header
    WHERE Store_ID = ? AND Business_Date = ? AND Is_Voided = false
""", [store_id, date])
 
# AFTER (BigQuery): named @param params, fully-qualified table names
result = db.query(f"""
    SELECT * FROM `{DS}.Sales_Transactions_Header`
    WHERE Store_ID = @store_id AND Business_Date = @target_date AND Is_Voided = FALSE
""", {"store_id": store_id, "target_date": date})
```
 
**Apply this pattern across ALL routers and the agent tools file.**
 
#### Files requiring this transformation:
 
| File | # of Queries | Special Considerations |
|------|-------------|----------------------|
| `routers/dashboard.py` | 8 queries | Use Python `datetime` for date math instead of `DATE_TRUNC` |
| `routers/workforce.py` | 12 queries | `DATE_TRUNC('week', ...)` → `DATE_TRUNC(date, WEEK(MONDAY))` |
| `routers/transactions.py` | 12 queries | `LIMIT {limit}` stays as f-string (can't parameterize LIMIT in BQ) |
| `routers/inventory.py` | 7 queries | `NULLIF()` works the same |
| `routers/weekly.py` | 10 queries | Week bounds calculated in Python already (no change needed) |
| `routers/chat.py` | 2 queries | Simple lookups |
| `agent/tools.py` | 15 queries | `DATE_TRUNC` and `INTERVAL` syntax changes |
 
#### Specific SQL Patterns to Watch For
 
**1. Date arithmetic (in `dashboard.py`, `workforce.py`, `tools.py`):**
 
```sql
-- DuckDB
SELECT DATE '2025-01-26' - INTERVAL 1 DAY
SELECT DATE_TRUNC('week', DATE '2025-01-26')
 
-- BigQuery
SELECT DATE_SUB(DATE '2025-01-26', INTERVAL 1 DAY)
SELECT DATE_TRUNC(DATE '2025-01-26', WEEK(MONDAY))
 
-- RECOMMENDED: Do date math in Python instead (avoids dialect issues)
from datetime import datetime, timedelta
dt = datetime.strptime(date, "%Y-%m-%d")
yesterday = (dt - timedelta(days=1)).strftime("%Y-%m-%d")
week_start = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
```
 
**2. EXTRACT (consistent across both, but capitalize in BQ for clarity):**
 
```sql
-- DuckDB
EXTRACT(hour FROM Open_Timestamp)
 
-- BigQuery (same syntax, conventionally uppercase)
EXTRACT(HOUR FROM Open_Timestamp)
```
 
**3. Boolean values:**
 
```sql
-- DuckDB
WHERE Is_Voided = false
 
-- BigQuery
WHERE Is_Voided = FALSE
```
 
**4. LIMIT with variables (in `transactions.py`, `tools.py`):**
 
```python
# DuckDB — LIMIT via f-string
db.query(f"... LIMIT {limit}", [store_id, date])
 
# BigQuery — same approach (LIMIT can't be parameterized with @param)
db.query(f"... LIMIT {limit}", {"store_id": store_id, "target_date": date})
```
 
**5. Timestamp string slicing (in `workforce.py`, `tools.py`):**
 
DuckDB returns Python `datetime` objects. BigQuery Python client also returns `datetime` objects — so `str(r["Shift_Start"])[11:16]` behaves the same.
 
### 2.6 Rewrite `agent/tools.py`
 
The agent tools file contains 15 SQL queries. Apply the same `?` → `@param` + table qualification pattern.
 
Example for the first tool function:
 
```python
DS = f"{settings.gcp_project_id}.{settings.bigquery_dataset}"
 
def _query_transactions(db, params: Dict) -> Dict:
    """Query transaction data."""
    store_id = params["store_id"]
    date = params["date"]
    aggregation = params.get("aggregation", "daily")
 
    if aggregation == "daily":
        result = db.query_one(f"""
            SELECT
                COUNT(*) as transactions,
                COALESCE(SUM(Total_Amount), 0) as revenue,
                COALESCE(AVG(Total_Amount), 0) as avg_ticket,
                COUNT(DISTINCT Employee_ID) as employees
            FROM `{DS}.Sales_Transactions_Header`
            WHERE Store_ID = @store_id
              AND Business_Date = @target_date
              AND Is_Voided = FALSE
        """, {"store_id": store_id, "target_date": date})
        # ... return same dict structure ...
```
 
**Special case — DATE_TRUNC in `_check_compliance`:**
 
```python
# DuckDB version:
week_start = db.query_scalar(f"SELECT DATE_TRUNC('week', DATE '{date}')")
 
# BigQuery — do it in Python instead:
from datetime import datetime, timedelta
dt = datetime.strptime(date, "%Y-%m-%d")
week_start = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
```
 
### 2.7 Update `main.py` (Serve Static Files)
 
**File:** `backend/app/main.py`
 
```python
"""FastAPI application entry point for Swig GM Dashboard."""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
 
from .routers import dashboard, transactions, workforce, chat, inventory, weekly
from .config import settings
 
app = FastAPI(
    title="Swig GM Dashboard API",
    description="API for the Swig General Manager AI Agent Dashboard",
    version="1.0.0"
)
 
# CORS — in production frontend is same origin; only needed for local dev
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# Include routers
app.include_router(dashboard.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(workforce.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(weekly.router, prefix="/api")
 
 
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "data_date": settings.data_current_date}
 
 
# ---- Serve React frontend in production ----
STATIC_DIR = Path(__file__).parent.parent / "static"
 
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")
 
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for any non-API route."""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        return {"message": "Swig GM Dashboard API", "version": "1.0.0", "docs": "/docs"}
 
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
 
### 2.8 Update `.env.example`
 
**File:** `backend/.env.example`
 
```env
# OpenAI (required for AI agent)
OPENAI_API_KEY=sk-your-key-here
 
# GCP / BigQuery
GCP_PROJECT_ID=swig-gm-dashboard
BIGQUERY_DATASET=swig_operations
 
# Application
DATA_CURRENT_DATE=2025-01-26
DEBUG=false
 
# CORS (for local dev, comma-separated)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```
 
---
 
## Phase 3: Containerize the Application
 
### 3.1 Dockerfile
 
**File:** `swig-gm-dashboard/Dockerfile`
 
```dockerfile
# ============================================
# Stage 1: Build the React frontend
# ============================================
FROM node:20-alpine AS frontend-build
 
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --production=false
COPY frontend/ ./
RUN npm run build
 
# ============================================
# Stage 2: Python backend + serve static files
# ============================================
FROM python:3.11-slim AS production
 
WORKDIR /app
 
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*
 
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
 
COPY backend/app ./app
COPY --from=frontend-build /app/frontend/dist ./static
 
# NOTE: No DuckDB file needed — data lives in BigQuery
 
ENV GCP_PROJECT_ID=swig-gm-dashboard
ENV BIGQUERY_DATASET=swig_operations
ENV DATA_CURRENT_DATE=2025-01-26
ENV PORT=8080
 
STOPSIGNAL SIGTERM
EXPOSE 8080
 
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1
 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
```
 
### 3.2 `.dockerignore`
 
**File:** `swig-gm-dashboard/.dockerignore`
 
```
frontend/node_modules/
backend/venv/
backend/__pycache__/
.git
.gitignore
*.md
.env
.env.*
.vscode/
.idea/
frontend/dist/
swig_operations.duckdb
bigquery/
```
 
---
 
## Phase 4: GCP Project Setup
 
### 4.1 Create Project and Enable APIs
 
```bash
export GCP_PROJECT_ID="swig-gm-dashboard"
export GCP_REGION="us-central1"
 
gcloud projects create $GCP_PROJECT_ID --name="Swig GM Dashboard" 2>/dev/null || true
gcloud config set project $GCP_PROJECT_ID
 
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    bigquery.googleapis.com
```
 
### 4.2 Create Artifact Registry
 
```bash
gcloud artifacts repositories create swig-dashboard \
    --repository-format=docker \
    --location=$GCP_REGION \
    --description="Swig GM Dashboard container images"
```
 
### 4.3 Store OpenAI Key in Secret Manager
 
```bash
echo -n "sk-your-actual-key" | \
    gcloud secrets create openai-api-key \
    --replication-policy="automatic" \
    --data-file=-
```
 
### 4.4 Create a Dedicated Service Account
 
```bash
gcloud iam service-accounts create swig-dashboard-sa \
    --display-name="Swig Dashboard Service Account"
 
SA_EMAIL="swig-dashboard-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
 
# Grant BigQuery read access
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/bigquery.dataViewer"
 
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/bigquery.jobUser"
 
# Grant Secret Manager access
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/secretmanager.secretAccessor"
```
 
---
 
## Phase 5: Deploy to Cloud Run
 
### 5.1 Build and Push
 
```bash
cd swig-gm-dashboard/
 
gcloud builds submit \
    --tag ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/swig-dashboard/swig-gm:latest \
    --timeout=15m
```
 
### 5.2 Deploy
 
```bash
SA_EMAIL="swig-dashboard-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
 
gcloud run deploy swig-gm-dashboard \
    --image ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/swig-dashboard/swig-gm:latest \
    --region $GCP_REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 2 \
    --timeout 300 \
    --concurrency 80 \
    --service-account $SA_EMAIL \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID},BIGQUERY_DATASET=swig_operations,DATA_CURRENT_DATE=2025-01-26" \
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```
 
**Flag explanations:**
 
| Flag | Value | Why |
|------|-------|-----|
| `--min-instances 0` | Scale to zero | $0 when idle |
| `--max-instances 2` | Cap scaling | Prevent cost spikes |
| `--memory 512Mi` | Sufficient | No embedded DB, lower memory is fine |
| `--timeout 300` | 5 minutes | OpenAI calls can be slow |
| `--service-account` | Dedicated SA | Least-privilege: BQ read + secret access only |
| `--set-secrets` | Secret Manager | Injects OPENAI_API_KEY securely |
 
### 5.3 Verify
 
```bash
SERVICE_URL=$(gcloud run services describe swig-gm-dashboard \
    --region $GCP_REGION \
    --format 'value(status.url)')
 
echo "Dashboard: $SERVICE_URL"
echo "API Docs:  $SERVICE_URL/docs"
echo "Health:    $SERVICE_URL/api/health"
 
curl $SERVICE_URL/api/health
curl "$SERVICE_URL/api/dashboard/stores"
curl "$SERVICE_URL/api/dashboard/kpis?store_id=1001"
```
 
### 5.4 Cold Start Behavior
 
| Component | Time |
|-----------|------|
| Container pull | ~2-3s (cached after first) |
| Python + BigQuery client init | ~1-2s |
| First BigQuery query | ~1-2s |
| **Total cold start** | **~4-7s** |
 
Slightly slower than the DuckDB version (~3-5s) due to BigQuery network round-trip. Acceptable for a demo. Set `--min-instances 1` (~$6/month) to eliminate cold starts.
 
---
 
## Phase 6: CI/CD (Optional)
 
### `cloudbuild.yaml`
 
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/swig-dashboard/swig-gm:${SHORT_SHA}',
           '-t', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/swig-dashboard/swig-gm:latest', '.']
    dir: 'swig-gm-dashboard'
 
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', '--all-tags', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/swig-dashboard/swig-gm']
 
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args: ['run', 'deploy', 'swig-gm-dashboard',
           '--image', '${_REGION}-docker.pkg.dev/${PROJECT_ID}/swig-dashboard/swig-gm:${SHORT_SHA}',
           '--region', '${_REGION}', '--platform', 'managed']
 
substitutions:
  _REGION: 'us-central1'
 
options:
  logging: CLOUD_LOGGING_ONLY
timeout: '900s'
```
 
---
 
## Security Considerations
 
1. **OpenAI key**: Stored in Secret Manager, injected at runtime — never in source or Docker image
2. **BigQuery access**: Dedicated service account with `bigquery.dataViewer` + `bigquery.jobUser` (read-only, can't modify schema or delete data)
3. **HTTPS**: Cloud Run provides managed TLS certificates automatically
4. **No SQL injection**: BigQuery parameterized queries (`@param`) prevent injection
5. **Public access**: `--allow-unauthenticated` is appropriate for a demo. Remove for restricted access.
 
---
 
## SQL Migration Reference
 
### Quick-Reference: Every SQL Pattern Change
 
```
┌─────────────────────────────────────────────────────────────────┐
│  FIND (DuckDB)                    │  REPLACE (BigQuery)          │
├───────────────────────────────────┼──────────────────────────────┤
│  db.query("...", [a, b])          │  db.query("...", {"a": a})   │
│  WHERE col = ?                    │  WHERE col = @param_name     │
│  true / false                     │  TRUE / FALSE                │
│  FROM TableName                   │  FROM `{DS}.TableName`       │
│  EXTRACT(hour FROM ts)            │  EXTRACT(HOUR FROM ts)       │
│  DATE_TRUNC('week', d)            │  DATE_TRUNC(d, WEEK(MONDAY)) │
│  DATE 'x' - INTERVAL 1 DAY       │  DATE_SUB(DATE 'x', INT 1 DAY)│
│  (or use Python datetime instead) │  (recommended approach)      │
└───────────────────────────────────┴──────────────────────────────┘
```
 
---
 
## Complete File Change Manifest
 
### New Files to Create
 
| File | Purpose |
|------|---------|
| `swig-gm-dashboard/Dockerfile` | Multi-stage build (React + FastAPI) |
| `swig-gm-dashboard/.dockerignore` | Exclude dev files from Docker context |
| `swig-gm-dashboard/bigquery/create_tables.sql` | BigQuery DDL for 20 tables |
| `swig-gm-dashboard/bigquery/load_data.py` | DuckDB → BigQuery data migration script |
| `swig-gm-dashboard/cloudbuild.yaml` | CI/CD pipeline (optional) |
| `swig-gm-dashboard/deploy.sh` | One-shot deploy convenience script |
 
### Files to Modify
 
| File | Changes |
|------|---------|
| `backend/requirements.txt` | `duckdb` → `google-cloud-bigquery` |
| `backend/app/config.py` | Remove `duckdb_path`, add `gcp_project_id` + `bigquery_dataset` |
| `backend/app/database.py` | **Complete rewrite**: DuckDB singleton → BigQuery client with named params |
| `backend/app/main.py` | Add static file serving + SPA catch-all for production |
| `backend/app/routers/dashboard.py` | 8 queries: `?` → `@param`, table names qualified, `FALSE` |
| `backend/app/routers/workforce.py` | 12 queries: same pattern + `DATE_TRUNC` change |
| `backend/app/routers/transactions.py` | 12 queries: same pattern |
| `backend/app/routers/inventory.py` | 7 queries: same pattern |
| `backend/app/routers/weekly.py` | 10 queries: same pattern |
| `backend/app/routers/chat.py` | 2 queries: same pattern |
| `backend/app/agent/tools.py` | 15 queries: same pattern + date math in Python |
| `backend/.env.example` | Updated environment variables |
 
### Files Unchanged
 
| File | Why |
|------|-----|
| `frontend/*` (all files) | No changes needed — `API_BASE = '/api'` works as-is |
| `backend/app/agent/gm_agent.py` | No SQL queries — uses tools.py |
| `backend/app/agent/prompts.py` | No database interaction |
 
### Total Query Count Requiring Migration
 
| File | Queries |
|------|---------|
| `routers/dashboard.py` | 8 |
| `routers/workforce.py` | 12 |
| `routers/transactions.py` | 12 |
| `routers/inventory.py` | 7 |
| `routers/weekly.py` | 10 |
| `routers/chat.py` | 2 |
| `agent/tools.py` | 15 |
| **Total** | **66 queries** |
 
---
 
## Deployment Checklist
 
### One-Time Setup
- [ ] Create GCP project, enable billing
- [ ] `gcloud` CLI installed and authenticated
- [ ] Enable APIs (Cloud Run, Artifact Registry, Secret Manager, BigQuery)
- [ ] Create BigQuery dataset (`swig_operations`)
- [ ] Run `bigquery/create_tables.sql` to create schema
- [ ] Run `bigquery/load_data.py` to load data from DuckDB
- [ ] Verify data: `bq query "SELECT COUNT(*) FROM swig_operations.Sales_Transactions_Header"`
- [ ] Store OpenAI key in Secret Manager
- [ ] Create dedicated service account with BQ + Secret access
- [ ] Create Artifact Registry repository
 
### Code Changes
- [ ] Update `requirements.txt` (duckdb → google-cloud-bigquery)
- [ ] Rewrite `config.py`
- [ ] Rewrite `database.py` (BigQuery client)
- [ ] Update `main.py` (static file serving)
- [ ] Migrate all 66 SQL queries across 7 files
- [ ] Update `.env.example`
- [ ] Test locally with BigQuery credentials
 
### Deploy
- [ ] Create `Dockerfile` and `.dockerignore`
- [ ] Build and push container image
- [ ] Deploy to Cloud Run
- [ ] Verify health: `curl $SERVICE_URL/api/health`
- [ ] Verify stores: `curl $SERVICE_URL/api/dashboard/stores`
- [ ] Verify frontend loads
- [ ] Test AI chat
- [ ] Set up $10/month billing alert
 
---
 
## Quick Deploy Script
 
**File:** `swig-gm-dashboard/deploy.sh`
 
```bash
#!/bin/bash
set -euo pipefail
 
GCP_PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
GCP_REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="swig-gm-dashboard"
IMAGE="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/swig-dashboard/swig-gm"
SA_EMAIL="swig-dashboard-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
 
echo "==> Building and pushing container image..."
gcloud builds submit \
    --tag "${IMAGE}:latest" \
    --timeout=15m \
    --project="${GCP_PROJECT_ID}"
 
echo "==> Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
    --image "${IMAGE}:latest" \
    --region "${GCP_REGION}" \
    --project "${GCP_PROJECT_ID}" \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 2 \
    --timeout 300 \
    --concurrency 80 \
    --service-account "${SA_EMAIL}" \
    --set-env-vars "GCP_PROJECT_ID=${GCP_PROJECT_ID},BIGQUERY_DATASET=swig_operations,DATA_CURRENT_DATE=2025-01-26" \
    --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
 
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
    --region "${GCP_REGION}" \
    --project "${GCP_PROJECT_ID}" \
    --format 'value(status.url)')
 
echo ""
echo "==> Deployment complete!"
echo "    Dashboard: ${SERVICE_URL}"
echo "    API Docs:  ${SERVICE_URL}/docs"
echo "    Health:    ${SERVICE_URL}/api/health"
```
 
---
 
## Local Development with BigQuery
 
```bash
# Authenticate with your Google account
gcloud auth application-default login
 
# Set environment
export GCP_PROJECT_ID="swig-gm-dashboard"
export BIGQUERY_DATASET="swig_operations"
export OPENAI_API_KEY="sk-..."
export DATA_CURRENT_DATE="2025-01-26"
 
# Start backend
cd swig-gm-dashboard/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
 
# Start frontend (separate terminal)
cd swig-gm-dashboard/frontend
npm install && npm run dev
```
 
---
 
## Teardown
 
```bash
gcloud run services delete swig-gm-dashboard --region=$GCP_REGION --quiet
bq rm -r -f ${GCP_PROJECT_ID}:swig_operations
gcloud secrets delete openai-api-key --quiet
gcloud artifacts docker images delete \
    ${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/swig-dashboard/swig-gm --quiet
# Optional: delete entire project
gcloud projects delete $GCP_PROJECT_ID
```