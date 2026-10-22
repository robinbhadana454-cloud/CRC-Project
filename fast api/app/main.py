from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import auth_router, admin_router, trains_router, bookings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager: initializes database and seed data on startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "### RailConnect Mini Railway Booking System API\n\n"
        "Connects passengers and railway administrators:\n"
        "- **Accounts**: Register, login with JWT tokens, logout with server-side revocation, forgot & reset password.\n"
        "- **Admin Control**: Manage stations, trains, timings, base fares, and seat inventories.\n"
        "- **Train Discovery**: Search routes, check dates, view real-time available seats and fares.\n"
        "- **Ticketing & PNR**: Atomic ticket booking with optimistic concurrency control, seat number allocation, "
        "and safe cancellation with seat restoration."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)
app.include_router(trains_router, prefix=settings.API_V1_PREFIX)
app.include_router(bookings_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root():
    """Welcome endpoint providing service status and quick links."""
    return {
        "service": settings.PROJECT_NAME,
        "status": "operational",
        "documentation": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
        "endpoints": {
            "auth": f"{settings.API_V1_PREFIX}/auth",
            "admin": f"{settings.API_V1_PREFIX}/admin",
            "trains": f"{settings.API_V1_PREFIX}/trains",
            "bookings": f"{settings.API_V1_PREFIX}/bookings",
        },
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Healthcheck endpoint for monitoring systems."""
    return {"status": "healthy"}
