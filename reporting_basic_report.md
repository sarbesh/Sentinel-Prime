# Sentinel Prime - Basic Reporting Implementation

## Overview
Implemented a new HTML report generation engine as part of the SENTINEL PRIME Basic Reporting module. This engine allows users to generate and download professionally formatted HTML reports for system summaries, individual network scans, and security events (alerts and honeypot activities).

## Implementation Details

### 1. Directory Structure
Created a new directory `backend/reports/` to house the reporting logic:
- `backend/reports/generator.py`: Core logic for fetching data from the database and rendering HTML.
- `backend/reports/templates/`: Jinja2 HTML templates for different report types.
- `backend/reports/output/`: Storage for generated HTML report files.

### 2. Report Types
Implemented three primary report types:
- **System Summary Report**: Provides a high-level overview of the system, including total device count, recent scan counts, active alert counts, and critical vulnerability counts. Includes a list of recent alerts and recent scans.
- **Network Scan Report**: A detailed report for a specific scan, including target information, scan type, status, and a full list of vulnerabilities discovered during that scan.
- **Security Events Report**: Consolidates security-related events, including system/IPS/IDS alerts and honeypot activity (source/destination IP, protocol, service, etc.).

### 3. Technology Stack
- **Template Engine**: `Jinja2` for dynamic HTML generation.
- **Data Access**: `SQLModel` (built on SQLAlchemy) to query existing models.
- **Web Framework**: `FastAPI` for the API endpoints.
- **Response Type**: `FileResponse` to facilitate direct browser downloads of the generated HTML files.

### 4. API Endpoints
Added a new router `api/reports.py` with the following endpoints:
- `GET /reports/summary`: Triggers generation and downloads a System Summary HTML report.
- `GET /reports/scan/{scan_id}`: Triggers generation and downloads an HTML report for the specified scan ID.
- `GET /reports/security-events?days={n}`: Triggers generation and downloads a Security Events HTML report for the last `n` days (default 7).

### 5. Data Models Used
The reporting engine leverages the following models from `models.py`:
- `Device` (for summary and scan details)
- `Scan` (for summary and scan details)
- `Vulnerability` (for scan-specific reports)
- `Alert` (for summary and security event reports)
- `HoneypotEvent` (for security event reports)
- `ScanData` (if needed for enhanced scan details)

## How to Test
1. Ensure the backend is running.
2. Use a tool like `curl` or a browser to access the endpoints:
   - `curl -O http://localhost:8000/reports/summary`
   - `curl -O http://localhost:8000/reports/scan/1`
   - `curl -O http://localhost:8000/reports/security-events?days=3`
3. Verify the downloaded `.html` files open correctly in a web browser and contain relevant data.

## Future Enhancements
- PDF report generation using `weasyprint` or `xhtml2pdf`.
- Email notifications with attached reports.
- Scheduling of automated reports (e.g., weekly summary).
- Custom report templates/styles.
