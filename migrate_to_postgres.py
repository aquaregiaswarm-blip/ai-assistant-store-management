"""Migrate Swig data from DuckDB to PostgreSQL."""
import duckdb
import psycopg2
from psycopg2.extras import execute_values
from decimal import Decimal
from datetime import date, datetime, time
import json

# Configuration
DUCKDB_PATH = "swig_data_generator/swig_operations.duckdb"
PG_CONFIG = {
    "host": "34.74.169.146",
    "port": 5432,
    "database": "swig",
    "user": "postgres",
    "password": "swig-postgres-2026",
}

# DuckDB type to PostgreSQL type mapping
TYPE_MAP = {
    "VARCHAR": "TEXT",
    "INTEGER": "INTEGER",
    "BIGINT": "BIGINT",
    "DOUBLE": "DOUBLE PRECISION",
    "DECIMAL": "NUMERIC",
    "BOOLEAN": "BOOLEAN",
    "DATE": "DATE",
    "TIME": "TIME",
    "TIMESTAMP": "TIMESTAMP",
    "UUID": "UUID",
}

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


def get_pg_type(duckdb_type: str) -> str:
    """Convert DuckDB type to PostgreSQL type."""
    # Handle parameterized types like DECIMAL(10,2)
    base_type = duckdb_type.split("(")[0].upper()
    
    # Keep precision for DECIMAL/NUMERIC
    if base_type in ("DECIMAL", "NUMERIC"):
        if "(" in duckdb_type:
            return f"NUMERIC{duckdb_type[duckdb_type.index('('):]}"
        return "NUMERIC"
    
    return TYPE_MAP.get(base_type, "TEXT")


def convert_value(val):
    """Convert Python value for PostgreSQL insertion."""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (date, datetime, time)):
        return val
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float, str)):
        return val
    return str(val)


def migrate():
    """Migrate all tables from DuckDB to PostgreSQL."""
    print("Connecting to DuckDB...")
    duck = duckdb.connect(DUCKDB_PATH, read_only=True)
    
    print("Connecting to PostgreSQL...")
    pg = psycopg2.connect(**PG_CONFIG)
    pg.autocommit = False
    cur = pg.cursor()
    
    for table in TABLES:
        print(f"\n{'='*50}")
        print(f"Migrating: {table}")
        print("="*50)
        
        # Get schema from DuckDB
        try:
            schema_query = f"DESCRIBE {table}"
            schema = duck.execute(schema_query).fetchall()
        except Exception as e:
            print(f"  SKIP: Table not found ({e})")
            continue
        
        # Build CREATE TABLE statement
        columns = []
        col_names = []
        for row in schema:
            col_name = row[0]
            col_type = row[1]
            pg_type = get_pg_type(col_type)
            nullable = "NULL" if row[3] == "YES" else "NOT NULL"
            # Make all columns nullable for simplicity
            columns.append(f'"{col_name}" {pg_type}')
            col_names.append(col_name)
        
        # Drop and create table
        drop_sql = f'DROP TABLE IF EXISTS "{table}" CASCADE'
        create_sql = f'CREATE TABLE "{table}" (\n  ' + ",\n  ".join(columns) + "\n)"
        
        print(f"  Creating table with {len(columns)} columns...")
        cur.execute(drop_sql)
        cur.execute(create_sql)
        
        # Get data from DuckDB
        data = duck.execute(f"SELECT * FROM {table}").fetchall()
        print(f"  Loading {len(data)} rows...")
        
        if data:
            # Convert values
            converted_data = [
                tuple(convert_value(v) for v in row)
                for row in data
            ]
            
            # Bulk insert
            placeholders = ",".join(["%s"] * len(col_names))
            col_list = ",".join([f'"{c}"' for c in col_names])
            insert_sql = f'INSERT INTO "{table}" ({col_list}) VALUES %s'
            
            execute_values(cur, insert_sql, converted_data, page_size=1000)
        
        pg.commit()
        print(f"  OK: {len(data)} rows loaded")
    
    # Create indexes for common queries
    print("\n" + "="*50)
    print("Creating indexes...")
    print("="*50)
    
    indexes = [
        ('idx_transactions_store_date', 'Sales_Transactions_Header', 'store_id, transaction_date'),
        ('idx_transactions_date', 'Sales_Transactions_Header', 'transaction_date'),
        ('idx_line_items_txn', 'Sales_Order_Line_Items', 'transaction_id'),
        ('idx_line_items_product', 'Sales_Order_Line_Items', 'product_sku'),
        ('idx_employees_store', 'Employee_Master_Profile', 'home_store_id'),
        ('idx_schedules_store_date', 'Labor_Schedules_Published', 'store_id, shift_date'),
        ('idx_attendance_employee', 'Time_Attendance_Actuals', 'employee_id'),
        ('idx_inventory_store', 'Inventory_Item_Master', 'store_id'),
        ('idx_inventory_ledger_store', 'Inventory_Transactions_Ledger', 'store_id, transaction_date'),
        ('idx_cash_recon_store', 'Daily_Cash_Reconciliation', 'store_id, business_date'),
    ]
    
    for idx_name, table, cols in indexes:
        try:
            cur.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON "{table}" ({cols})')
            print(f"  Created {idx_name}")
        except Exception as e:
            print(f"  SKIP {idx_name}: {e}")
    
    pg.commit()
    
    # Verify counts
    print("\n" + "="*50)
    print("Verification:")
    print("="*50)
    
    for table in TABLES:
        try:
            duck_count = duck.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            cur.execute(f'SELECT COUNT(*) FROM "{table}"')
            pg_count = cur.fetchone()[0]
            status = "✓" if duck_count == pg_count else "✗"
            print(f"  {status} {table}: {pg_count} rows")
        except Exception as e:
            print(f"  ? {table}: {e}")
    
    cur.close()
    pg.close()
    duck.close()
    
    print("\n" + "="*50)
    print("Migration complete!")
    print("="*50)


if __name__ == "__main__":
    migrate()
