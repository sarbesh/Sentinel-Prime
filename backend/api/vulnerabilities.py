from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database import get_session
from models import Vulnerability, VulnerabilitySeverity

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])


@router.get("", response_model=List[Vulnerability])
def list_vulnerabilities(
    device_id: Optional[int] = None,
    severity: Optional[VulnerabilitySeverity] = None,
    session: Session = Depends(get_session)
):
    """List all vulnerabilities, optionally filtered by device or severity."""
    query = select(Vulnerability).order_by(Vulnerability.discovered_at.desc())
    if device_id:
        query = query.where(Vulnerability.device_id == device_id)
    if severity:
        query = query.where(Vulnerability.severity == severity)
    return session.exec(query).all()


@router.get("/{vuln_id}", response_model=Vulnerability)
def get_vulnerability(vuln_id: int, session: Session = Depends(get_session)):
    """Get a specific vulnerability by ID."""
    vuln = session.get(Vulnerability, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln


@router.post("/{vuln_id}/acknowledge")
def acknowledge_vulnerability(vuln_id: int, session: Session = Depends(get_session)):
    """Acknowledge a vulnerability."""
    vuln = session.get(Vulnerability, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    vuln.acknowledged = True
    session.add(vuln)
    session.commit()
    session.refresh(vuln)
    return {"status": "acknowledged", "id": vuln_id}


@router.delete("/{vuln_id}")
def delete_vulnerability(vuln_id: int, session: Session = Depends(get_session)):
    """Delete a vulnerability record."""
    vuln = session.get(Vulnerability, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    session.delete(vuln)
    session.commit()
    return {"message": "Vulnerability deleted successfully"}