import os
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(prefix="/downloads", tags=["downloads"])

DOWNLOADS_DIR = "/app/downloads"


class DownloadItem(BaseModel):
    id: str
    name: str
    filename: str
    size: Optional[int] = None
    platform: str
    description: str


AVAILABLE_DOWNLOADS = {
    "android": {
        "id": "android",
        "name": "Android APK",
        "filename": "sentinel-prime-android.apk",
        "platform": "android",
        "description": "Install on Android devices",
    },
    "ios": {
        "id": "ios",
        "name": "iOS App",
        "filename": "sentinel-prime-ios.ipa",
        "platform": "ios",
        "description": "Install on iPhone/iPad",
    },
    "windows": {
        "id": "windows",
        "name": "Windows",
        "filename": "Sentinel-Prime-Setup.exe",
        "platform": "windows",
        "description": "Windows 10/11 x64",
    },
    "linux": {
        "id": "linux",
        "name": "Linux",
        "filename": "sentinel-prime-linux.AppImage",
        "platform": "linux",
        "description": "Linux AppImage",
    },
}


@router.get("", response_model=List[DownloadItem])
def list_downloads():
    downloads = []
    if not os.path.exists(DOWNLOADS_DIR):
        return downloads
    
    for platform, info in AVAILABLE_DOWNLOADS.items():
        filepath = os.path.join(DOWNLOADS_DIR, info["filename"])
        size = None
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
        
        downloads.append(DownloadItem(
            id=info["id"],
            name=info["name"],
            filename=info["filename"],
            size=size,
            platform=info["platform"],
            description=info["description"],
        ))
    
    return downloads


@router.get("/{filename}")
def download_file(filename: str):
    filepath = os.path.join(DOWNLOADS_DIR, filename)
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    return FileResponse(filepath, filename=filename)
