import os
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter(prefix="/updates", tags=["updates"])

APP_VERSION = "1.0.0"
UPDATE_BASE_URL = os.environ.get("UPDATE_BASE_URL", "http://localhost:3000/downloads")


class UpdateInfo(BaseModel):
    version: str
    release_date: str
    release_notes: Optional[str] = None
    download_url: str
    mandatory: bool = False
    min_platform_version: Optional[str] = None


class UpdateCheckResponse(BaseModel):
    update_available: bool
    current_version: str
    update: Optional[UpdateInfo] = None


@router.get("/check", response_model=UpdateCheckResponse)
def check_for_updates(platform: str = "android", current_version: str = APP_VERSION):
    """
    Check if an update is available for the app.
    
    Args:
        platform: The platform (android, ios, windows, linux)
        current_version: The current app version
    """
    available_updates = {
        "android": UpdateInfo(
            version="1.0.0",
            release_date="2026-03-05",
            release_notes="Initial release with device monitoring, alerts, and honeypot features.",
            download_url=f"{UPDATE_BASE_URL}/sentinel-prime-android.apk",
            mandatory=False,
        ),
        "ios": UpdateInfo(
            version="1.0.0",
            release_date="2026-03-05",
            release_notes="Initial release with device monitoring, alerts, and honeypot features.",
            download_url=f"{UPDATE_BASE_URL}/sentinel-prime-ios.ipa",
            mandatory=False,
        ),
        "windows": UpdateInfo(
            version="1.0.0",
            release_date="2026-03-05",
            release_notes="Initial release with device monitoring, alerts, and honeypot features.",
            download_url=f"{UPDATE_BASE_URL}/Sentinel-Prime-Setup.exe",
            mandatory=False,
        ),
        "linux": UpdateInfo(
            version="1.0.0",
            release_date="2026-03-05",
            release_notes="Initial release with device monitoring, alerts, and honeypot features.",
            download_url=f"{UPDATE_BASE_URL}/sentinel-prime-linux.AppImage",
            mandatory=False,
        ),
    }

    update = available_updates.get(platform)
    
    if not update:
        return UpdateCheckResponse(
            update_available=False,
            current_version=current_version,
        )

    needs_update = _compare_versions(update.version, current_version) > 0

    return UpdateCheckResponse(
        update_available=needs_update,
        current_version=current_version,
        update=update if needs_update else None,
    )


def _compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.
    Returns: 1 if version1 > version2, -1 if version1 < version2, 0 if equal
    """
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))
    
    for i in range(max_len):
        if v1_parts[i] > v2_parts[i]:
            return 1
        elif v1_parts[i] < v2_parts[i]:
            return -1
    return 0


@router.get("/latest")
def get_latest_version(platform: str = "android"):
    """Get the latest version info for a platform."""
    check_result = check_for_updates(platform=platform)
    return check_result.update
