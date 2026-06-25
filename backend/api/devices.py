from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pyoui import OUI

from database import get_session
from models import Device, DeviceStatus, DeviceType

router = APIRouter(prefix="/devices", tags=["devices"])

def lookup_vendor(mac: Optional[str]) -> Optional[str]:
    if not mac:
        return None
    try:
        return OUI(mac).vendor
    except Exception:
        return "Unknown Vendor"

def fingerprint_os(scan_results: Optional[str]) -> Optional[str]:
    if not scan_results:
        return "Unknown"
    
    results = scan_results.lower()
    if "microsoft" in results or "windows" in results:
        return "Windows"
    if "linux" in results or "ubuntu" in results or "debian" in results:
        return "Linux"
    if "apple" in results or "darwin" in results or "ios" in results:
        return "Apple/iOS"
    if "android" in results:
        return "Android"
    return "Unknown"

def profile_device(device: Device) -> Optional[str]:
    # Basic profiling based on type and vendor
    type_str = device.type.value
    vendor_str = device.vendor or "Unknown"
    
    if type_str == DeviceType.ROUTER:
        return f"Network Infrastructure ({vendor_str})"
    if type_str == DeviceType.PHONE:
        return f"Mobile Device ({vendor_str})"
    if type_str == DeviceType.COMPUTER or type_str == DeviceType.LAPTOP:
        return f"Computing Endpoint ({vendor_str})"
    return f"Generic Device ({vendor_str})"

@router.get("", response_model=List[Device])
def list_devices(session: Session = Depends(get_session)):
    """List all devices."""
    return session.exec(select(Device)).all()


@router.get("/{device_id}", response_model=Device)
def get_device(device_id: int, session: Session = Depends(get_session)):
    """Get a specific device by ID."""
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("", response_model=Device)
def create_device(device: Device, session: Session = Depends(get_session)):
    """Create a new device."""
    if device.mac_address:
        device.vendor = lookup_vendor(device.mac_address)
    
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.put("/{device_id}", response_model=Device)
def update_device(
    device_id: int, device_update: Device, session: Session = Depends(get_session)
):
    """Update an existing device."""
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    update_data = device_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)

    if device.mac_address:
        device.vendor = lookup_vendor(device.mac_address)

    device.last_seen = datetime.utcnow()
    session.add(device)
    session.commit()
    session.refresh(device)
    return device


@router.delete("/{device_id}")
def delete_device(device_id: int, session: Session = Depends(get_session)):
    """Delete a device."""
    device = session.get(Device, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    session.delete(device)
    session.commit()
    return {"message": "Device deleted successfully"}


@router.get("/ip/{ip_address}", response_model=Device)
def get_device_by_ip(ip_address: str, session: Session = Depends(get_session)):
    """Get a device by IP address."""
    device = session.exec(
        select(Device).where(Device.ip_address == ip_address)
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.get("/mac/{mac_address}", response_model=Device)
def get_device_by_mac(mac_address: str, session: Session = Depends(get_session)):
    """Get a device by MAC address."""
    device = session.exec(
        select(Device).where(Device.mac_address == mac_address)
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
