from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import Alert, AlertSeverity

router = APIRouter(prefix="/alerts", tags=["alerts"])


class IDSAlertRequest(BaseModel):
    timestamp: str
    source_ip: str
    source_port: int
    dest_ip: str
    dest_port: int
    protocol: str
    signature: str
    signature_id: int
    severity: int
    category: str | None = None
    raw_event: str | None = None


@router.post("/ids-alerts", response_model=Alert)
def create_ids_alert(alert_req: IDSAlertRequest, session: Session = Depends(get_session)):
    """Create a new IDS alert from Suricata."""
    severity_map = {
        1: AlertSeverity.CRITICAL,
        2: AlertSeverity.HIGH,
        3: AlertSeverity.MEDIUM,
        4: AlertSeverity.LOW,
    }
    severity = severity_map.get(alert_req.severity, AlertSeverity.LOW)

    try:
        alert_timestamp = datetime.fromisoformat(alert_req.timestamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        alert_timestamp = datetime.utcnow()

    alert = Alert(
        source="ids",
        severity=severity,
        title=alert_req.signature,
        description=f"{alert_req.protocol} {alert_req.source_ip}:{alert_req.source_port} -> {alert_req.dest_ip}:{alert_req.dest_port}",
        signature_id=alert_req.signature_id,
        timestamp=alert_timestamp,
        raw_log=alert_req.raw_event,
    )
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


@router.get("", response_model=List[Alert])
def list_alerts(
    acknowledged: bool | None = None, session: Session = Depends(get_session)
):
    """List all alerts, optionally filtered by acknowledged status."""
    query = select(Alert).order_by(Alert.timestamp.desc())
    if acknowledged is not None:
        query = query.where(Alert.acknowledged == acknowledged)
    return session.exec(query).all()


@router.get("/{alert_id}", response_model=Alert)
def get_alert(alert_id: int, session: Session = Depends(get_session)):
    """Get a specific alert by ID."""
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("", response_model=Alert)
def create_alert(alert: Alert, session: Session = Depends(get_session)):
    """Create a new alert."""
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


@router.put("/{alert_id}/acknowledge", response_model=Alert)
def acknowledge_alert(alert_id: int, session: Session = Depends(get_session)):
    """Acknowledge an alert."""
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, session: Session = Depends(get_session)):
    """Delete an alert."""
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    session.delete(alert)
    session.commit()
    return {"message": "Alert deleted successfully"}
