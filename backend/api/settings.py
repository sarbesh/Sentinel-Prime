from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import Settings

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsResponse(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SettingsUpdate(BaseModel):
    value: str


@router.get("", response_model=List[SettingsResponse])
def list_settings(session: Session = Depends(get_session)):
    """List all settings."""
    return session.exec(select(Settings)).all()


@router.get("/{key}", response_model=SettingsResponse)
def get_setting(key: str, session: Session = Depends(get_session)):
    """Get a specific setting."""
    setting = session.exec(select(Settings).where(Settings.key == key)).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    return setting


@router.post("")
def update_setting(setting: SettingsResponse, session: Session = Depends(get_session)):
    """Create or update a setting."""
    existing = session.exec(select(Settings).where(Settings.key == setting.key)).first()
    
    if existing:
        existing.value = setting.value
        if setting.description:
            existing.description = setting.description
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    else:
        new_setting = Settings(
            key=setting.key,
            value=setting.value,
            description=setting.description,
        )
        session.add(new_setting)
        session.commit()
        session.refresh(new_setting)
        return new_setting


@router.delete("/{key}")
def delete_setting(key: str, session: Session = Depends(get_session)):
    """Delete a setting."""
    setting = session.exec(select(Settings).where(Settings.key == key)).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    session.delete(setting)
    session.commit()
    return {"status": "deleted", "key": key}
