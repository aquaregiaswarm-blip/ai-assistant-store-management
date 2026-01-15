"""DuckDB database connection and query utilities."""
import duckdb
from typing import Any, List, Dict, Optional
from contextlib import contextmanager
from .config import settings


class Database:
    """DuckDB connection manager."""

    _instance: Optional["Database"] = None
    _conn: Optional[duckdb.DuckDBPyConnection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> duckdb.DuckDBPyConnection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = duckdb.connect(settings.duckdb_path, read_only=True)
        return self._conn

    def query(self, sql: str, params: List[Any] = None) -> List[Dict]:
        """Execute a query and return results as list of dicts."""
        conn = self.connect()
        if params:
            result = conn.execute(sql, params)
        else:
            result = conn.execute(sql)

        columns = [desc[0] for desc in result.description]
        rows = result.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    def query_one(self, sql: str, params: List[Any] = None) -> Optional[Dict]:
        """Execute a query and return a single result."""
        results = self.query(sql, params)
        return results[0] if results else None

    def query_scalar(self, sql: str, params: List[Any] = None) -> Any:
        """Execute a query and return a single scalar value."""
        conn = self.connect()
        if params:
            result = conn.execute(sql, params).fetchone()
        else:
            result = conn.execute(sql).fetchone()
        return result[0] if result else None


# Global database instance
db = Database()


def get_db() -> Database:
    """Dependency injection for database."""
    return db
