import asyncio
import json
from typing import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette import EventSourceResponse
from sqlmodel import Session, select

from database import get_session
from models import User, Alert, Device
from api.auth import get_current_user

router = APIRouter(prefix="/sse", tags=["sse"])

subscribers: dict[str, list[asyncio.Queue]] = {
    "alerts": [],
    "devices": [],
    "scans": [],
}


async def alert_generator(user: User) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()
    subscribers["alerts"].append(queue)
    try:
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    finally:
        subscribers["alerts"].remove(queue)


async def device_generator(user: User) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()
    subscribers["devices"].append(queue)
    try:
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    finally:
        subscribers["devices"].remove(queue)


async def scan_generator(user: User) -> AsyncGenerator[str, None]:
    queue = asyncio.Queue()
    subscribers["scans"].append(queue)
    try:
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    finally:
        subscribers["scans"].remove(queue)


@router.get("/alerts")
async def sse_alerts(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    async def stream():
        queue = asyncio.Queue()
        subscribers["alerts"].append(queue)
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in subscribers["alerts"]:
                subscribers["alerts"].remove(queue)

    return EventSourceResponse(stream())


@router.get("/devices")
async def sse_devices(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    async def stream():
        queue = asyncio.Queue()
        subscribers["devices"].append(queue)
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in subscribers["devices"]:
                subscribers["devices"].remove(queue)

    return EventSourceResponse(stream())


@router.get("/scans")
async def sse_scans(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    async def stream():
        queue = asyncio.Queue()
        subscribers["scans"].append(queue)
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if queue in subscribers["scans"]:
                subscribers["scans"].remove(queue)

    return EventSourceResponse(stream())


def broadcast_alert(alert_data: dict):
    event = {
        "type": "alert",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    for queue in subscribers["alerts"]:
        asyncio.create_task(queue.put(event))


def broadcast_device(device_data: dict):
    event = {
        "type": "device",
        "data": device_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    for queue in subscribers["devices"]:
        asyncio.create_task(queue.put(event))


def broadcast_scan(scan_data: dict):
    event = {
        "type": "scan",
        "data": scan_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
    for queue in subscribers["scans"]:
        asyncio.create_task(queue.put(event))
