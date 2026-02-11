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
