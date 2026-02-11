"""Export data from DuckDB and load into BigQuery."""
import duckdb
import json
import subprocess
import tempfile
import os
from pathlib import Path
from decimal import Decimal

# Configuration
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "../../swig_data_generator/swig_operations.duckdb")
GCP_PROJECT = os.getenv("GCP_PROJECT_ID", "prj-cts-lab-vertex-sandbox")
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
    import sys
    db_path = Path(__file__).parent / DUCKDB_PATH
    print(f"Connecting to DuckDB: {db_path.resolve()}", flush=True)
    conn = duckdb.connect(str(db_path.resolve()), read_only=True)
    print("Connected!", flush=True)

    for table in TABLES:
        print(f"\n--- {table} ---", flush=True)

        # Check if table exists
        try:
            result = conn.execute(f"SELECT * FROM {table} LIMIT 0")
        except Exception as e:
            print(f"  SKIP: Table not found ({e})")
            continue

        # Export to temporary JSONL file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as f:
            tmpfile = f.name

            # Get rows as dicts
            result = conn.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()

            print(f"  Exporting {len(rows)} rows...", flush=True)

            for row in rows:
                record = {}
                for col, val in zip(columns, row):
                    if val is None:
                        record[col] = None
                    elif isinstance(val, Decimal):
                        record[col] = float(val)
                    elif hasattr(val, "isoformat"):
                        record[col] = val.isoformat()
                    elif isinstance(val, (int, float, bool, str)):
                        record[col] = val
                    else:
                        record[col] = str(val)
                f.write(json.dumps(record) + "\n")

        # Load into BigQuery using bq CLI
        destination = f"{GCP_PROJECT}:{BQ_DATASET}.{table}"
        print(f"  Loading into {destination}...", flush=True)

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
