from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import engine, Base
from app.modules.dhcp_listener import listener
from app.modules.threat_intel_updater import updater
from app.modules.mcp import server as mcp_server
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import API routers
from api import alerts, auth, devices, honeypot, scans, reports, vulnerabilities
from api import downloads, todos, version, settings as settings_api, sse, ips, network, websocket

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SENTINEL PRIME Backend")

# Add CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)},
    )

# Include MCP router
app.include_router(mcp_server.router)

# Include API routers
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(honeypot.router)
app.include_router(scans.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(downloads.router)
app.include_router(todos.router)
app.include_router(version.router)
app.include_router(settings_api.router)
app.include_router(sse.router)
app.include_router(ips.router)
app.include_router(network.router)
app.include_router(vulnerabilities.router)

# Include WebSocket router for real-time updates
websocket.setup_websocket(app)

# Include routers or start background tasks
@app.on_event("startup")
async def startup_event():
    # Start DHCP listener in background
    asyncio.create_task(listener.start_listener())
    # Start threat intelligence updater in background
    asyncio.create_task(updater.start_updater())

@app.get("/")
async def root():
    return {"message": "SENTINEL PRIME Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}