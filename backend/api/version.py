import os
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Header

router = APIRouter(prefix="/version", tags=["version"])

CURRENT_VERSION = "1.0.0"
EXPECTED_UI_SHA = os.getenv("UI_VERSION_SHA", "dev")


class VersionInfo(BaseModel):
    version: str
    sha: Optional[str] = None
    update_available: bool = False
    mandatory: bool = False
    message: Optional[str] = None


def get_current_version() -> VersionInfo:
    return VersionInfo(
        version=CURRENT_VERSION,
        sha=EXPECTED_UI_SHA,
    )


@router.get("/check", response_model=VersionInfo)
def check_version(x_ui_version: Optional[str] = Header(None, alias="X-UI-Version")):
    """
    Check if client UI version is up to date.
    
    Client should send X-UI-Version header with their current SHA/version.
    """
    current = get_current_version()
    
    if x_ui_version and x_ui_version != EXPECTED_UI_SHA:
        current.update_available = True
        current.message = "A new version of the UI is available. Please refresh to update."
    
    return current


@router.get("/current", response_model=VersionInfo)
def get_current_version_info():
    """Get current UI version info."""
    return get_current_version()
