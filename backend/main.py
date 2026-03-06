from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import alerts, devices, honeypot, scans
from api.auth import router as auth_router
from api.downloads import router as downloads_router
from api.updates import router as updates_router
from api.todos import router as todos_router
from database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Sentinel Prime Backend",
    description="API for home network security monitoring",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(devices.router)
app.include_router(scans.router)
app.include_router(alerts.router)
app.include_router(honeypot.router)
app.include_router(downloads_router)
app.include_router(updates_router)
app.include_router(todos_router)


@app.get("/")
def read_root():
    return {"msg": "Sentinel Prime Backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
