import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader
from sqlmodel import Session, select, desc
from models import Device, Scan, Vulnerability, Alert, HoneypotEvent, ScanData, ScanType, ScanStatus, VulnerabilitySeverity, AlertSeverity, ThreatIntelSource

REPORTS_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(REPORTS_DIR, "templates")
OUTPUT_DIR = os.path.join(REPORTS_DIR, "output")

class ReportGenerator:
    def __init__(self, session: Session):
        self.session = session
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)

    def _get_base_context(self) -> Dict[str, Any]:
        return {
            "generation_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "year": datetime.utcnow().year
        }

    def generate_system_summary(self) -> str:
        """Generates a system summary report."""
        summary = {
            "total_devices": self.session.exec(select(Device)).count(),
            "recent_scans_count": self.session.exec(select(Scan).limit(10)).count(),
            "active_alerts_count": self.session.exec(select(Alert).where(Alert.acknowledged == False)).count(),
            "critical_vulns_count": self.session.exec(select(Vulnerability).where(Vulnerability.severity == "critical")).count(),
        }

        alerts = self.session.exec(
            select(Alert).order_by(desc(Alert.timestamp)).limit(10)
        ).all()

        scans = self.session.exec(
            select(Scan).order_by(desc(Scan.started_at)).limit(5)
        ).all()

        template = self.env.get_template("system_summary.html")
        html = template.render(
            **self._get_base_context(),
            summary=summary,
            alerts=alerts,
            scans=scans
        )
        
        filename = f"system_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(html)
        
        return filepath

    def generate_network_scan(self, scan_id: int) -> str:
        """Generates a report for a specific scan."""
        scan = self.session.get(Scan, scan_id)
        if not scan:
            raise ValueError(f"Scan with ID {scan_id} not found.")

        vulnerabilities = self.session.exec(
            select(Vulnerability).where(Vulnerability.scan_id == scan_id)
        ).all()

        template = self.env.get_template("network_scan.html")
        html = template.render(
            **self._get_base_context(),
            scan=scan,
            vulnerabilities=vulnerabilities,
            raw_output=scan.raw_output
        )
        
        filename = f"scan_{scan_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(html)
            
        return filepath

    def generate_security_events(self, days: int = 7) -> str:
        """Generates a report of security events (alerts and honeypot events)."""
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)

        alerts = self.session.exec(
            select(Alert).where(Alert.timestamp >= since).order_by(desc(Alert.timestamp))
        ).all()

        honeypot_events = self.session.exec(
            select(HoneypotEvent).where(HoneypotEvent.timestamp >= since).order_by(desc(HoneypotEvent.timestamp))
        ).all()

        template = self.env.get_template("security_events.html")
        html = template.render(
            **self._get_base_context(),
            alerts=alerts,
            honeypot_events=honeypot_events
        )

        filename = f"security_events_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w") as f:
            f.write(html)

        return filepath
