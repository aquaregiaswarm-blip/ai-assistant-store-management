from .dashboard import router as dashboard_router
from .transactions import router as transactions_router
from .workforce import router as workforce_router
from .chat import router as chat_router

__all__ = ["dashboard_router", "transactions_router", "workforce_router", "chat_router"]
