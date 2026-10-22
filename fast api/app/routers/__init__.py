from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.trains import router as trains_router
from app.routers.bookings import router as bookings_router

__all__ = [
    "auth_router",
    "admin_router",
    "trains_router",
    "bookings_router",
]
