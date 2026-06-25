from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from sqlmodel import Session
from database import get_session
from reports.generator import ReportGenerator
import os

router = APIRouter(prefix="/reports", tags=["Reports"])

REPORTS_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "output")

@router.get("/summary", response_class=FileResponse)
async def get_summary_report(session: Session = Depends(get_session)):
    """
    Generates and downloads a system summary report.
    """
    try:
        generator = ReportGenerator(session)
        file_path = generator.generate_system_summary()
        
        # Determine filename for content-disposition if needed, or just let FileResponse handle it
        filename = os.path.basename(file_path)
        return FileResponse(path=file_path, filename=filename, media_type='text/html')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary report: {str(e)}")

@router.get("/scan/{scan_id}", response_class=FileResponse)
async def get_scan_report(scan_id: int, session: Session = Depends(get_session)):
    """
    Generates and downloads a report for a specific scan.
    """
    try:
        generator = ReportGenerator(session)
        file_path = generator.generate_network_scan(scan_id)
        
        filename = os.path.basename(file_path)
        return FileResponse(path=file_path, filename=filename, media_type='text/html')
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate scan report: {str(e)}")

@router.get("/security-events", response_class=FileResponse)
async def get_security_events_report(
    days: int = Query(7, ge=1, le=365), 
    session: Session = Depends(get_session)
):
    """
    Generates and downloads a security events report (alerts and honeypot events).
    """
    try:
        generator = ReportGenerator(session)
        file_path = generator.generate_security_events(days=days)
        
        filename = os.path.basename(file_path)
        return FileResponse(path=file_path, filename=filename, media_type='text/html')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate security events report: {str(e)}")
