"""PostgreSQL database connection and query utilities."""
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Dict, List, Optional
from contextlib import contextmanager
from .config import settings


class Database:
    """PostgreSQL connection manager.

    Provides query()/query_one()/query_scalar() interface for the routers.
    Uses connection pooling pattern with context manager.
    """

    _instance: Optional["Database"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @contextmanager
    def _get_connection(self):
        """Get a database connection with automatic cleanup."""
        conn = psycopg2.connect(settings.database_url)
        try:
            yield conn
        finally:
            conn.close()

    def query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Execute a query and return results as list of dicts.

        Args:
            sql: SQL query string using %(param_name)s for parameters.
            params: Dict of parameter name -> value. Example:
                    {"store_id": 1001, "target_date": "2025-01-26"}
        """
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return [dict(row) for row in cur.fetchall()]

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
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                return row[0] if row else None


# Global database instance
db = Database()


def get_db() -> Database:
    """Dependency injection for database."""
    return db
