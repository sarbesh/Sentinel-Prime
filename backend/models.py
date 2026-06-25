from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class DeviceType(str, Enum):
    UNKNOWN = "unknown"
    ROUTER = "router"
    COMPUTER = "computer"
    LAPTOP = "laptop"
    PHONE = "phone"
    TABLET = "tablet"
    IOT = "iot"
    SERVER = "server"
    TV = "tv"
    PRINTER = "printer"
    GAMING = "gaming"
    OTHER = "other"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class Device(SQLModel, table=True):
    __tablename__ = "devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    mac_address: str = Field(unique=True, index=True, nullable=False)  # FIX: MAC is now required & unique identifier
    name: str
    ip_address: Optional[str] = None  # Changed to Optional - IP can change
    type: DeviceType = Field(default=DeviceType.UNKNOWN)
    vendor: Optional[str] = None
    status: DeviceStatus = Field(default=DeviceStatus.UNKNOWN)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    hostname: Optional[str] = None
    os: Optional[str] = None  # FIX: Track OS deviations
    notes: Optional[str] = None
    
    # Track IP address history for anomaly detection
    last_known_ip: Optional[str] = None
    
    class Config:
        # Ensure MAC address is always indexed for fast lookups
        schema_extra = {
            "example": {
                "mac_address": "00:1A:2B:3C:4D:5E",
                "name": "My iPhone",
                "ip_address": "192.168.0.105",
                "os": "iOS 17",
                "type": "phone",
                "status": "online"
            }
        }


class ScanType(str, Enum):
    QUICK = "quick"
    FULL = "full"
    PORT = "port"
    VULN = "vuln"
    PING = "ping"
    DEEP = "deep"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class VulnerabilitySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Vulnerability(SQLModel, table=True):
    __tablename__ = "vulnerabilities"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    scan_id: Optional[int] = Field(default=None, foreign_key="scans.id")
    cve_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: VulnerabilitySeverity
    cvss_score: Optional[float] = None
    service: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    exploit_available: bool = Field(default=False)
    exploit_details: Optional[str] = None
    remediation: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = Field(default=False)


class ScanData(SQLModel, table=True):
    __tablename__ = "scan_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    mac_address: str
    ip_address: str
    scan_type: str
    raw_data: str
    services_json: Optional[str] = None
    vulnerabilities_json: Optional[str] = None
    ai_vector_ready: bool = Field(default=False)
    ai_summary: Optional[str] = None
    os_detection: Optional[str] = None
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    port_count: int = Field(default=0)
    vuln_count: int = Field(default=0)
    critical_vuln_count: int = Field(default=0)
    scanned_at: datetime = Field(default_factory=datetime.utcnow)


class Scan(SQLModel, table=True):
    __tablename__ = "scans"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    scan_type: ScanType = Field(default=ScanType.QUICK)
    target: str
    status: ScanStatus = Field(default=ScanStatus.PENDING)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    results: Optional[str] = None
    raw_output: Optional[str] = None
    hosts_discovered: int = Field(default=0)  # FIX Issue 2: Track discovered hosts
    failed_hosts: int = Field(default=0)  # FIX Issue 2: Track failed attempts
    error_message: Optional[str] = None  # FIX Issue 2: Store error messages


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"

    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[int] = Field(default=None, foreign_key="devices.id")
    source: str
    severity: AlertSeverity
    title: str
    description: Optional[str] = None
    signature_id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = Field(default=False)
    raw_log: Optional[str] = None


class HoneypotEvent(SQLModel, table=True):
    __tablename__ = "honeypot_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    honeypot_type: str
    source_ip: str
    source_port: Optional[int] = None
    destination_ip: str
    destination_port: int
    protocol: Optional[str] = None
    service: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Optional[str] = None
    raw_log: Optional[str] = None


class ThreatIntelSource(str, Enum):
    OTX = "otx"
    ABUSEIPDB = "abuseipdb"
    VIRUSTOTAL = "virustotal"
    MANUAL = "manual"


class ThreatIntel(SQLModel, table=True):
    __tablename__ = "threat_intel"

    id: Optional[int] = Field(default=None, primary_key=True)
    indicator: str
    indicator_type: str
    source: ThreatIntelSource
    confidence: int
    threat_type: Optional[str] = None
    description: Optional[str] = None
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    tags: Optional[str] = None
    active: bool = Field(default=True)


class NetworkInterface(SQLModel, table=True):
    __tablename__ = "network_interfaces"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    interface_type: Optional[str] = None
    is_monitored: bool = Field(default=False)


class Settings(SQLModel, table=True):
    __tablename__ = "settings"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True)
    value: str
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: Optional[str] = Field(default=None, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    role: str = Field(default="user")
    permissions: Optional[str] = None
    is_verified: bool = Field(default=False)
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Token(SQLModel, table=True):
    __tablename__ = "tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    token: str = Field(unique=True)
    token_type: str = Field(default="access")
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Todo(SQLModel, table=True):
    __tablename__ = "todos"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: str = Field(default="medium")
    category: Optional[str] = None
    completed: bool = Field(default=False)
    snoozed_until: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
