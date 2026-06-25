import json
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from database import get_session
from models import User, Alert, Device
from api.auth import get_current_user
from api.sse import broadcast_alert

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ips", tags=["ips-ids"])

IPS_RULES = [
    {"id": "sig-001", "name": "Brute Force SSH", "category": "authentication", "severity": "high", "pattern": r"Failed password for.*ssh", "action": "alert", "description": "Detects SSH brute force attempts"},
    {"id": "sig-002", "name": "Port Scan Detection", "category": "reconnaissance", "severity": "medium", "pattern": r"Connection refused|Connection timed out", "action": "alert", "description": "Detects port scanning activity"},
    {"id": "sig-003", "name": "SQL Injection Attempt", "category": "injection", "severity": "critical", "pattern": r"(union|select|insert|delete|drop).*from", "action": "block", "description": "Detects SQL injection attempts"},
    {"id": "sig-004", "name": "XSS Attempt", "category": "injection", "severity": "high", "pattern": r"<script|javascript:|onerror=", "action": "block", "description": "Detects cross-site scripting attempts"},
    {"id": "sig-005", "name": "Suspicious User Agent", "category": "reconnaissance", "severity": "low", "pattern": r"(nikto|sqlmap|nmap|masscan)", "action": "alert", "description": "Detects known scanning tools"},
    {"id": "sig-006", "name": "Default Credentials", "category": "authentication", "severity": "critical", "pattern": r"(admin|root):(admin|root|password)", "action": "block", "description": "Detects default credential usage"},
    {"id": "sig-007", "name": "DDoS SYN Flood", "category": "dos", "severity": "critical", "pattern": r"SYN.*SYN.*SYN", "action": "block", "description": "Detects SYN flood attacks"},
    {"id": "sig-008", "name": "ICMP Flood", "category": "dos", "severity": "high", "pattern": r"ICMP.*echo request", "action": "alert", "description": "Detects ICMP flood attempts"},
    {"id": "sig-009", "name": "DNS Zone Transfer", "category": "reconnaissance", "severity": "medium", "pattern": r"AXFR|zone transfer", "action": "alert", "description": "Detects DNS zone transfer requests"},
    {"id": "sig-010", "name": "SMB Exploit Attempt", "category": "exploit", "severity": "critical", "pattern": r"(ms08_067|eternalblue|wannacry)", "action": "block", "description": "Detects known SMB exploits"},
]

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"

CVE_DATABASE = {
    "CVE-2024-0001": {"severity": "critical", "cvss": 9.8, "description": "Remote code execution via buffer overflow", "affected": "Network Scanner <= 1.2"},
    "CVE-2024-0002": {"severity": "high", "cvss": 8.1, "description": "SQL injection in login form", "affected": "Web App <= 2.0"},
    "CVE-2024-0003": {"severity": "medium", "cvss": 6.5, "description": "Cross-site scripting vulnerability", "affected": "Admin Panel <= 1.5"},
    "CVE-2024-0004": {"severity": "critical", "cvss": 9.1, "description": "Authentication bypass", "affected": "Auth Service <= 3.0"},
    "CVE-2024-0005": {"severity": "high", "cvss": 7.5, "description": "Denial of service via malformed packet", "affected": "Network Stack <= 4.2"},
    "CVE-2023-1234": {"severity": "critical", "cvss": 10.0, "description": "EternalBlue-like SMB vulnerability", "affected": "Windows SMB <= 1.3"},
    "CVE-2023-5678": {"severity": "high", "cvss": 8.6, "description": "Remote code execution in SSH daemon", "affected": "OpenSSH <= 8.2"},
    "CVE-2023-9999": {"severity": "medium", "cvss": 5.3, "description": "Information disclosure via debug endpoint", "affected": "API Gateway <= 2.1"},
}

COMMON_VULNERABLE_SERVICES = {
    "ssh": {"ports": [22], "vulns": ["CVE-2023-5678"], "recommendation": "Update OpenSSH to latest version, use key-based auth"},
    "ftp": {"ports": [21], "vulns": ["CVE-2024-0001"], "recommendation": "Disable FTP, use SFTP instead"},
    "http": {"ports": [80, 8080], "vulns": ["CVE-2024-0002", "CVE-2024-0003"], "recommendation": "Enable HTTPS, sanitize inputs, use WAF"},
    "smb": {"ports": [445, 139], "vulns": ["CVE-2023-1234"], "recommendation": "Disable SMBv1, apply MS patches"},
    "mysql": {"ports": [3306], "vulns": ["CVE-2024-0004"], "recommendation": "Restrict access, use strong passwords"},
    "postgres": {"ports": [5432], "vulns": [], "recommendation": "Enable SSL, restrict network access"},
    "redis": {"ports": [6379], "vulns": ["CVE-2024-0005"], "recommendation": "Bind to localhost, require authentication"},
    "elasticsearch": {"ports": [9200], "vulns": ["CVE-2023-9999"], "recommendation": "Enable X-Pack security, disable debug"},
    "rdesktop": {"ports": [3389], "vulns": ["CVE-2023-1234"], "recommendation": "Use VPN, enable NLA"},
    "telnet": {"ports": [23], "vulns": ["CVE-2024-0001"], "recommendation": "Disable telnet immediately"},
}


class IPSRule(BaseModel):
    id: str
    name: str
    category: str
    severity: str
    pattern: str
    action: str
    description: str
    enabled: bool = True


class VulnerabilityInfo(BaseModel):
    cve_id: str
    severity: str
    cvss: float
    description: str
    affected: str
    recommendation: str


class IDSAlert(BaseModel):
    id: Optional[int] = None
    timestamp: Optional[datetime] = None
    source_ip: str
    dest_ip: str
    rule_id: str
    rule_name: str
    severity: str
    category: str
    description: str
    action_taken: str
    raw_log: str


@router.get("/rules", response_model=List[dict])
def get_ips_rules(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    enabled: Optional[bool] = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get all IPS/IDS rules with optional filtering."""
    rules = IPS_RULES.copy()
    
    if category:
        rules = [r for r in rules if r["category"] == category]
    if severity:
        rules = [r for r in rules if r["severity"] == severity]
    
    return rules


@router.get("/rules/{rule_id}")
def get_rule(
    rule_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get a specific IPS rule."""
    rule = next((r for r in IPS_RULES if r["id"] == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.post("/rules/{rule_id}/toggle")
def toggle_rule(
    rule_id: str,
    enabled: bool,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Enable or disable an IPS rule."""
    rule = next((r for r in IPS_RULES if r["id"] == rule_id), None)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule["enabled"] = enabled
    return {"id": rule_id, "enabled": enabled}


@router.get("/alerts", response_model=List[IDSAlert])
def get_ids_alerts(
    limit: int = 50,
    severity: Optional[str] = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get IDS alerts."""
    alerts = session.exec(
        select(Alert).where(Alert.source == "ids").order_by(Alert.timestamp.desc()).limit(limit)
    ).all()
    
    result = []
    for alert in alerts:
        result.append(IDSAlert(
            id=alert.id,
            timestamp=alert.timestamp,
            source_ip=alert.source,
            dest_ip=alert.title,
            rule_id="manual",
            rule_name=alert.title,
            severity=alert.severity,
            category="manual",
            description=alert.description or "",
            action_taken="logged",
            raw_log=alert.description or "",
        ))
    
    if severity:
        result = [a for a in result if a.severity == severity]
    
    return result


@router.post("/analyze")
def analyze_traffic(
    request: dict,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Analyze network traffic against IPS rules."""
    source_ip = request.get("source_ip", "")
    dest_ip = request.get("dest_ip", "")
    payload = request.get("payload", "")
    
    matched_rules = []
    for rule in IPS_RULES:
        if not rule.get("enabled", True):
            continue
        import re
        if re.search(rule["pattern"], payload, re.IGNORECASE):
            matched_rules.append(rule)
    
    if matched_rules:
        for rule in matched_rules:
            alert = Alert(
                title=rule["name"],
                description=f"Source: {source_ip}, Dest: {dest_ip}",
                severity=rule["severity"],
                source="ips",
                source_ip=source_ip,
            )
            session.add(alert)
            session.commit()
            
            broadcast_alert({
                "id": alert.id,
                "title": alert.title,
                "severity": alert.severity,
                "source_ip": source_ip,
                "dest_ip": dest_ip,
                "rule_id": rule["id"],
            })
    
    return {
        "analyzed": True,
        "source_ip": source_ip,
        "dest_ip": dest_ip,
        "matched_rules": len(matched_rules),
        "rules": matched_rules,
    }


@router.get("/vulnerabilities/{cve_id}", response_model=VulnerabilityInfo)
def get_vulnerability(
    cve_id: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get vulnerability information from the local database."""
    cve_id = cve_id.upper()
    if cve_id not in CVE_DATABASE:
        raise HTTPException(status_code=404, detail="CVE not found in database")
    
    vuln = CVE_DATABASE[cve_id]
    return VulnerabilityInfo(
        cve_id=cve_id,
        severity=vuln["severity"],
        cvss=vuln["cvss"],
        description=vuln["description"],
        affected=vuln["affected"],
        recommendation=_get_recommendation(cve_id),
    )


@router.get("/vulnerabilities")
def get_all_vulnerabilities(
    severity: Optional[str] = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get all vulnerabilities in the database."""
    result = []
    for cve_id, vuln in CVE_DATABASE.items():
        if severity and vuln["severity"] != severity:
            continue
        result.append(VulnerabilityInfo(
            cve_id=cve_id,
            severity=vuln["severity"],
            cvss=vuln["cvss"],
            description=vuln["description"],
            affected=vuln["affected"],
            recommendation=_get_recommendation(cve_id),
        ))
    return result


@router.get("/services/vulnerabilities")
def get_service_vulnerabilities(
    service: str,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get known vulnerabilities for a specific service."""
    service = service.lower()
    if service not in COMMON_VULNERABLE_SERVICES:
        return {
            "service": service,
            "vulnerabilities": [],
            "recommendation": "No known vulnerabilities for this service",
            "ports": [],
        }
    
    service_info = COMMON_VULNERABLE_SERVICES[service]
    vulns = []
    for cve_id in service_info.get("vulns", []):
        if cve_id in CVE_DATABASE:
            vulns.append(VulnerabilityInfo(
                cve_id=cve_id,
                severity=CVE_DATABASE[cve_id]["severity"],
                cvss=CVE_DATABASE[cve_id]["cvss"],
                description=CVE_DATABASE[cve_id]["description"],
                affected=CVE_DATABASE[cve_id]["affected"],
                recommendation=_get_recommendation(cve_id),
            ))
    
    return {
        "service": service,
        "vulnerabilities": vulns,
        "recommendation": service_info["recommendation"],
        "ports": service_info["ports"],
    }


@router.get("/stats")
def get_ips_stats(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Get IPS/IDS statistics."""
    total_alerts = session.exec(
        select(Alert).where(Alert.source == "ids")
    ).count()
    
    critical = session.exec(
        select(Alert).where(Alert.source == "ids").where(Alert.severity == "critical")
    ).count()
    
    high = session.exec(
        select(Alert).where(Alert.source == "ids").where(Alert.severity == "high")
    ).count()
    
    medium = session.exec(
        select(Alert).where(Alert.source == "ids").where(Alert.severity == "medium")
    ).count()
    
    low = session.exec(
        select(Alert).where(Alert.source == "ids").where(Alert.severity == "low")
    ).count()
    
    return {
        "total_alerts": total_alerts,
        "by_severity": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        },
        "rules_count": len(IPS_RULES),
        "rules_enabled": len([r for r in IPS_RULES if r.get("enabled", True)]),
    }


def _get_recommendation(cve_id: str) -> str:
    """Get remediation recommendation for a CVE."""
    recommendations = {
        "CVE-2024-0001": "Update to latest version, disable root login, use fail2ban",
        "CVE-2024-0002": "Use parameterized queries, validate input, enable WAF",
        "CVE-2024-0003": "Sanitize user input, enable CSP headers",
        "CVE-2024-0004": "Update authentication module, enable MFA",
        "CVE-2024-0005": "Update network stack, implement rate limiting",
        "CVE-2023-1234": "Apply MS security patches, disable SMBv1",
        "CVE-2023-5678": "Update OpenSSH, use key-based authentication",
        "CVE-2023-9999": "Disable debug endpoints in production",
    }
    return recommendations.get(cve_id, "Apply latest security updates")
