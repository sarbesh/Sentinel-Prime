import json
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import User
from api.auth import get_current_user
from arp_monitor import scan_and_update_devices, start_arp_monitoring, get_arp_watcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/network", tags=["network"])

NETWORK_SCAN_INTERVAL = 60

class NetworkScanRequest(BaseModel):
    target: str
    scan_type: str = "arp"


@router.post("/scan")
def trigger_network_scan(
    request: NetworkScanRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Trigger a network scan to detect devices via ARP."""
    logger.info(f"Manual network scan triggered for {request.target}")
    
    try:
        arp_table = scan_and_update_devices()
        
        return {
            "status": "success",
            "devices_found": len(arp_table),
            "devices": [{"ip": ip, "mac": mac} for ip, mac in arp_table.items()],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Network scan error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
def get_network_devices(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get all devices detected via ARP monitoring."""
    watcher = get_arp_watcher()
    arp_table = watcher.get_arp_table()
    
    return {
        "devices": [{"ip": ip, "mac": mac} for ip, mac in arp_table.items()],
        "monitoring": watcher.running,
    }


@router.post("/monitoring/start")
def start_monitoring(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Start ARP monitoring."""
    start_arp_monitoring()
    return {"status": "started", "message": "ARP monitoring started"}


@router.post("/monitoring/stop")
def stop_monitoring(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Stop ARP monitoring."""
    watcher = get_arp_watcher()
    watcher.stop()
    return {"status": "stopped", "message": "ARP monitoring stopped"}


@router.get("/monitoring/status")
def get_monitoring_status(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get ARP monitoring status."""
    watcher = get_arp_watcher()
    return {
        "running": watcher.running,
        "network": watcher.network,
        "known_devices": len(watcher.known_devices),
    }
