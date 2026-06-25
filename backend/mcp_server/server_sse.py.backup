import os
import sys
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from mcp.server import Server
from sse_starlette import EventSourceResponse
from sqlmodel import select, Session

from database import engine
from models import (
    Alert,
    AlertSeverity,
    Device,
    DeviceStatus,
    DeviceType,
    HoneypotEvent,
    Scan,
    ScanType,
    ScanStatus,
    Settings,
    Vulnerability,
    VulnerabilitySeverity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sentinel Prime MCP Server")

MCP_SERVER_NAME = "sentinel-prime-mcp"
mcp_server = Server(MCP_SERVER_NAME)

API_KEY_HEADER = "x-api-key"


def verify_api_key(api_key: Optional[str] = Header(None, alias=API_KEY_HEADER)) -> bool:
    if api_key is None:
        return False
    
    with Session(engine) as session:
        setting = session.exec(
            select(Settings).where(Settings.key == "mcp_api_key")
        ).first()
        
        if setting and setting.value == api_key:
            return True
        
        if api_key == os.getenv("MCP_API_KEY", "sentinel-prime-mcp-default"):
            return True
            
        return False


def require_api_key(api_key: Optional[str] = Header(None, alias=API_KEY_HEADER)):
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@mcp_server.list_tools()
async def list_tools() -> list[dict[str, Any]]:
    return [
        {
            "name": "list_devices",
            "description": "Get all network devices discovered on the network",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by status: online, offline, unknown",
                        "enum": ["online", "offline", "unknown"],
                    },
                    "device_type": {
                        "type": "string",
                        "description": "Filter by device type",
                        "enum": [
                            "router",
                            "computer",
                            "laptop",
                            "phone",
                            "tablet",
                            "iot",
                            "server",
                            "tv",
                            "printer",
                            "gaming",
                            "other",
                        ],
                    },
                },
            },
        },
        {
            "name": "get_device",
            "description": "Get details of a specific device by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "integer", "description": "The device ID"},
                },
                "required": ["device_id"],
            },
        },
        {
            "name": "get_device_by_ip",
            "description": "Get details of a specific device by IP address",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "ip_address": {"type": "string", "description": "The IP address"},
                },
                "required": ["ip_address"],
            },
        },
        {
            "name": "get_device_by_mac",
            "description": "Get details of a specific device by MAC address",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mac_address": {"type": "string", "description": "The MAC address"},
                },
                "required": ["mac_address"],
            },
        },
        {
            "name": "create_device",
            "description": "Add a new device to the network monitoring system",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Device name"},
                    "ip_address": {"type": "string", "description": "IP address"},
                    "mac_address": {"type": "string", "description": "MAC address"},
                    "device_type": {
                        "type": "string",
                        "description": "Device type",
                        "enum": ["router", "computer", "laptop", "phone", "tablet", "iot", "server", "tv", "printer", "gaming", "other"],
                    },
                    "vendor": {"type": "string", "description": "Device vendor"},
                    "hostname": {"type": "string", "description": "Device hostname"},
                    "os": {"type": "string", "description": "Operating system"},
                },
                "required": ["name", "ip_address"],
            },
        },
        {
            "name": "update_device",
            "description": "Update an existing device",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "integer", "description": "The device ID"},
                    "name": {"type": "string", "description": "Device name"},
                    "device_type": {"type": "string", "description": "Device type"},
                    "vendor": {"type": "string", "description": "Device vendor"},
                    "hostname": {"type": "string", "description": "Device hostname"},
                    "os": {"type": "string", "description": "Operating system"},
                    "notes": {"type": "string", "description": "Notes about the device"},
                },
                "required": ["device_id"],
            },
        },
        {
            "name": "delete_device",
            "description": "Delete a device from monitoring",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "integer", "description": "The device ID"},
                },
                "required": ["device_id"],
            },
        },
        {
            "name": "get_alerts",
            "description": "Get security alerts from the network monitoring system",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "acknowledged": {
                        "type": "boolean",
                        "description": "Filter by acknowledged status",
                    },
                    "severity": {
                        "type": "string",
                        "description": "Filter by severity level",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of alerts to return",
                        "default": 50,
                    },
                },
            },
        },
        {
            "name": "get_alert",
            "description": "Get a specific alert by ID",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "alert_id": {"type": "integer", "description": "The alert ID"},
                },
                "required": ["alert_id"],
            },
        },
        {
            "name": "create_alert",
            "description": "Create a new security alert",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "integer", "description": "Associated device ID"},
                    "source": {"type": "string", "description": "Alert source"},
                    "severity": {
                        "type": "string",
                        "description": "Alert severity",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "title": {"type": "string", "description": "Alert title"},
                    "description": {"type": "string", "description": "Alert description"},
                    "raw_log": {"type": "string", "description": "Raw log data"},
                },
                "required": ["source", "severity", "title"],
            },
        },
        {
            "name": "acknowledge_alert",
            "description": "Acknowledge a security alert",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "alert_id": {"type": "integer", "description": "The alert ID"},
                },
                "required": ["alert_id"],
            },
        },
        {
            "name": "trigger_scan",
            "description": "Trigger a network security scan on a target",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target IP address or network range",
                    },
                    "scan_type": {
                        "type": "string",
                        "description": "Type of scan to perform",
                        "enum": ["quick", "full", "port", "vuln", "ping", "deep"],
                        "default": "quick",
                    },
                    "ports": {"type": "string", "description": "Specific ports to scan"},
                },
                "required": ["target"],
            },
        },
        {
            "name": "get_scan",
            "description": "Get details of a specific scan",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "scan_id": {"type": "integer", "description": "The scan ID"},
                },
                "required": ["scan_id"],
            },
        },
        {
            "name": "list_scans",
            "description": "List all scans",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of scans", "default": 20},
                },
            },
        },
        {
            "name": "list_vulnerabilities",
            "description": "List vulnerabilities found on network devices",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "device_id": {"type": "integer", "description": "Filter by device ID"},
                    "severity": {
                        "type": "string",
                        "description": "Filter by severity",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                },
            },
        },
        {
            "name": "get_vulnerability",
            "description": "Get details of a specific vulnerability",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "vuln_id": {"type": "integer", "description": "The vulnerability ID"},
                },
                "required": ["vuln_id"],
            },
        },
        {
            "name": "acknowledge_vulnerability",
            "description": "Acknowledge a vulnerability",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "vuln_id": {"type": "integer", "description": "The vulnerability ID"},
                },
                "required": ["vuln_id"],
            },
        },
        {
            "name": "get_honeypot_events",
            "description": "Get honeypot detection events",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "honeypot_type": {"type": "string", "description": "Filter by honeypot type"},
                    "limit": {"type": "integer", "description": "Maximum number of events", "default": 50},
                },
            },
        },
        {
            "name": "get_network_status",
            "description": "Get overall network security status summary",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_settings",
            "description": "Get system settings",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Specific setting key to retrieve"},
                },
            },
        },
        {
            "name": "update_settings",
            "description": "Update system settings",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Setting key"},
                    "value": {"type": "string", "description": "Setting value"},
                    "description": {"type": "string", "description": "Setting description"},
                },
                "required": ["key", "value"],
            },
        },
    ]


def _serialize_device(device: Device) -> dict[str, Any]:
    return {
        "id": device.id,
        "name": device.name,
        "ip_address": device.ip_address,
        "mac_address": device.mac_address,
        "type": device.type.value if device.type else None,
        "vendor": device.vendor,
        "status": device.status.value if device.status else None,
        "hostname": device.hostname,
        "os": device.os,
        "notes": device.notes,
        "first_seen": device.first_seen.isoformat() if device.first_seen else None,
        "last_seen": device.last_seen.isoformat() if device.last_seen else None,
    }


def _serialize_alert(alert: Alert) -> dict[str, Any]:
    return {
        "id": alert.id,
        "device_id": alert.device_id,
        "source": alert.source,
        "severity": alert.severity.value if alert.severity else None,
        "title": alert.title,
        "description": alert.description,
        "timestamp": alert.timestamp.isoformat() if alert.timestamp else None,
        "acknowledged": alert.acknowledged,
    }


def _serialize_vulnerability(vuln: Vulnerability) -> dict[str, Any]:
    return {
        "id": vuln.id,
        "device_id": vuln.device_id,
        "scan_id": vuln.scan_id,
        "cve_id": vuln.cve_id,
        "title": vuln.title,
        "description": vuln.description,
        "severity": vuln.severity.value if vuln.severity else None,
        "cvss_score": vuln.cvss_score,
        "service": vuln.service,
        "port": vuln.port,
        "protocol": vuln.protocol,
        "exploit_available": vuln.exploit_available,
        "exploit_details": vuln.exploit_details,
        "remediation": vuln.remediation,
        "acknowledged": vuln.acknowledged,
        "discovered_at": vuln.discovered_at.isoformat() if vuln.discovered_at else None,
    }


def _serialize_honeypot_event(event: HoneypotEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "honeypot_type": event.honeypot_type,
        "source_ip": event.source_ip,
        "source_port": event.source_port,
        "destination_ip": event.destination_ip,
        "destination_port": event.destination_port,
        "protocol": event.protocol,
        "service": event.service,
        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        "details": event.details,
        "raw_log": event.raw_log,
    }


def _serialize_scan(scan: Scan) -> dict[str, Any]:
    return {
        "id": scan.id,
        "device_id": scan.device_id,
        "scan_type": scan.scan_type.value if scan.scan_type else None,
        "target": scan.target,
        "status": scan.status.value if scan.status else None,
        "started_at": scan.started_at.isoformat() if scan.started_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "raw_output": scan.raw_output,
    }


@mcp_server.call_tool()
async def call_tool(
    name: str, arguments: dict | None, session=None
) -> list[dict[str, Any]]:
    if arguments is None:
        arguments = {}

    use_own_session = session is None
    
    if use_own_session:
        session = Session(engine)
        should_commit = True
    else:
        should_commit = False

    try:
        if name == "list_devices":
            query = select(Device)
            if arguments.get("status"):
                query = query.where(Device.status == DeviceStatus(arguments["status"]))
            if arguments.get("device_type"):
                query = query.where(Device.type == DeviceType(arguments["device_type"]))
            devices = session.exec(query).all()
            return [_serialize_device(d) for d in devices]

        elif name == "get_device":
            device = session.get(Device, arguments["device_id"])
            if not device:
                return [{"error": "Device not found"}]
            return [_serialize_device(device)]

        elif name == "get_device_by_ip":
            device = session.exec(
                select(Device).where(Device.ip_address == arguments["ip_address"])
            ).first()
            if not device:
                return [{"error": "Device not found"}]
            return [_serialize_device(device)]

        elif name == "get_device_by_mac":
            device = session.exec(
                select(Device).where(Device.mac_address == arguments["mac_address"])
            ).first()
            if not device:
                return [{"error": "Device not found"}]
            return [_serialize_device(device)]

        elif name == "create_device":
            device = Device(
                name=arguments["name"],
                ip_address=arguments["ip_address"],
                mac_address=arguments.get("mac_address"),
                type=DeviceType(arguments.get("device_type", "unknown")),
                vendor=arguments.get("vendor"),
                hostname=arguments.get("hostname"),
                os=arguments.get("os"),
                status=DeviceStatus.UNKNOWN,
            )
            session.add(device)
            session.commit()
            session.refresh(device)
            return [_serialize_device(device)]

        elif name == "update_device":
            device = session.get(Device, arguments["device_id"])
            if not device:
                return [{"error": "Device not found"}]
            if "name" in arguments:
                device.name = arguments["name"]
            if "device_type" in arguments:
                device.type = DeviceType(arguments["device_type"])
            if "vendor" in arguments:
                device.vendor = arguments["vendor"]
            if "hostname" in arguments:
                device.hostname = arguments["hostname"]
            if "os" in arguments:
                device.os = arguments["os"]
            if "notes" in arguments:
                device.notes = arguments["notes"]
            session.commit()
            session.refresh(device)
            return [_serialize_device(device)]

        elif name == "delete_device":
            device = session.get(Device, arguments["device_id"])
            if not device:
                return [{"error": "Device not found"}]
            session.delete(device)
            session.commit()
            return [{"success": True, "message": "Device deleted"}]

        elif name == "get_alerts":
            query = select(Alert).order_by(Alert.timestamp.desc())
            if arguments.get("acknowledged") is not None:
                query = query.where(Alert.acknowledged == arguments["acknowledged"])
            if arguments.get("severity"):
                query = query.where(Alert.severity == AlertSeverity(arguments["severity"]))
            limit = arguments.get("limit", 50)
            query = query.limit(limit)
            alerts = session.exec(query).all()
            return [_serialize_alert(a) for a in alerts]

        elif name == "get_alert":
            alert = session.get(Alert, arguments["alert_id"])
            if not alert:
                return [{"error": "Alert not found"}]
            return [_serialize_alert(alert)]

        elif name == "create_alert":
            alert = Alert(
                device_id=arguments.get("device_id"),
                source=arguments["source"],
                severity=AlertSeverity(arguments["severity"]),
                title=arguments["title"],
                description=arguments.get("description"),
                raw_log=arguments.get("raw_log"),
            )
            session.add(alert)
            session.commit()
            session.refresh(alert)
            return [_serialize_alert(alert)]

        elif name == "acknowledge_alert":
            alert = session.get(Alert, arguments["alert_id"])
            if not alert:
                return [{"error": "Alert not found"}]
            alert.acknowledged = True
            session.commit()
            return [{"success": True, "alert_id": arguments["alert_id"]}]

        elif name == "trigger_scan":
            target = arguments["target"]
            scan_type_str = arguments.get("scan_type", "quick")
            ports = arguments.get("ports")
            
            scan = Scan(
                target=target,
                scan_type=ScanType(scan_type_str),
                status=ScanStatus.PENDING,
            )
            session.add(scan)
            session.commit()
            session.refresh(scan)
            
            # Wait for the scan to be processed by the scanner service
            start_time = time.time()
            timeout = 120  # seconds
            while time.time() - start_time < timeout:
                session.refresh(scan)
                if scan.status not in [ScanStatus.PENDING, ScanStatus.RUNNING]:
                    break
                time.sleep(5)
            
            # After waiting, check the final status
            if scan.status == ScanStatus.COMPLETED:
                return [
                    {
                        "scan_id": scan.id,
                        "target": scan.target,
                        "scan_type": scan.scan_type.value if scan.scan_type else None,
                        "status": scan.status.value if scan.status else None,
                        "message": "Scan completed successfully",
                    }
                ]
            elif scan.status == ScanStatus.FAILED:
                return [
                    {
                        "error": f"Scan failed: {scan.raw_output}",
                    }
                ]
            else:
                return [
                    {
                        "error": f"Scan timeout after {timeout} seconds",
                    }
                ]

        elif name == "get_scan":
            scan = session.get(Scan, arguments["scan_id"])
            if not scan:
                return [{"error": "Scan not found"}]
            return [_serialize_scan(scan)]

        elif name == "list_scans":
            query = select(Scan).order_by(Scan.started_at.desc())
            limit = arguments.get("limit", 20)
            query = query.limit(limit)
            scans = session.exec(query).all()
            return [_serialize_scan(s) for s in scans]

        elif name == "list_vulnerabilities":
            query = select(Vulnerability).order_by(Vulnerability.discovered_at.desc())
            if arguments.get("device_id"):
                query = query.where(Vulnerability.device_id == arguments["device_id"])
            if arguments.get("severity"):
                query = query.where(
                    Vulnerability.severity == VulnerabilitySeverity(arguments["severity"])
                )
            vulns = session.exec(query).all()
            return [_serialize_vulnerability(v) for v in vulns]

        elif name == "get_vulnerability":
            vuln = session.get(Vulnerability, arguments["vuln_id"])
            if not vuln:
                return [{"error": "Vulnerability not found"}]
            return [_serialize_vulnerability(vuln)]

        elif name == "acknowledge_vulnerability":
            vuln = session.get(Vulnerability, arguments["vuln_id"])
            if not vuln:
                return [{"error": "Vulnerability not found"}]
            vuln.acknowledged = True
            session.commit()
            return [{"success": True, "vuln_id": arguments["vuln_id"]}]

        elif name == "get_honeypot_events":
            query = select(HoneypotEvent).order_by(HoneypotEvent.timestamp.desc())
            if arguments.get("honeypot_type"):
                query = query.where(HoneypotEvent.honeypot_type == arguments["honeypot_type"])
            limit = arguments.get("limit", 50)
            query = query.limit(limit)
            events = session.exec(query).all()
            return [_serialize_honeypot_event(e) for e in events]

        elif name == "get_network_status":
            total_devices = session.exec(select(Device)).all()
            online_devices = [d for d in total_devices if d.status == DeviceStatus.ONLINE]
            unacknowledged_alerts = session.exec(
                select(Alert).where(Alert.acknowledged == False)
            ).all()
            critical_alerts = [a for a in unacknowledged_alerts if a.severity == AlertSeverity.CRITICAL]
            high_alerts = [a for a in unacknowledged_alerts if a.severity == AlertSeverity.HIGH]
            vulnerabilities = session.exec(select(Vulnerability)).all()
            critical_vulns = [v for v in vulnerabilities if v.severity == VulnerabilitySeverity.CRITICAL]
            honeypot_events = session.exec(
                select(HoneypotEvent).order_by(HoneypotEvent.timestamp.desc()).limit(10)
            ).all()

            return [
                {
                    "devices": {
                        "total": len(total_devices),
                        "online": len(online_devices),
                        "offline": len(total_devices) - len(online_devices),
                    },
                    "alerts": {
                        "unacknowledged": len(unacknowledged_alerts),
                        "critical": len(critical_alerts),
                        "high": len(high_alerts),
                    },
                    "vulnerabilities": {
                        "total": len(vulnerabilities),
                        "critical": len(critical_vulns),
                    },
                    "honeypot_events": {
                        "recent_count": len(honeypot_events),
                    },
                    "security_level": "critical"
                    if critical_alerts or critical_vulns
                    else "high"
                    if high_alerts
                    else "normal",
                }
            ]

        elif name == "get_settings":
            if arguments.get("key"):
                setting = session.exec(
                    select(Settings).where(Settings.key == arguments["key"])
                ).first()
                if setting:
                    return [{"key": setting.key, "value": setting.value, "description": setting.description}]
                return [{"error": "Setting not found"}]
            settings = session.exec(select(Settings)).all()
            return [{"key": s.key, "value": s.value, "description": s.description} for s in settings]

        elif name == "update_settings":
            key = arguments["key"]
            value = arguments["value"]
            description = arguments.get("description")
            
            setting = session.exec(select(Settings).where(Settings.key == key)).first()
            if setting:
                setting.value = value
                if description:
                    setting.description = description
            else:
                setting = Settings(key=key, value=value, description=description)
                session.add(setting)
            session.commit()
            return [{"success": True, "key": key}]

        else:
            return [{"error": f"Unknown tool: {name}"}]

    except Exception as e:
        logger.error(f"MCP tool error: {e}")
        if should_commit:
            session.rollback()
        return [{"error": str(e)}]
    finally:
        if use_own_session:
            session.close()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "sentinel-prime-mcp"}


@app.get("/mcp/{path:path}")
async def mcp_sse(
    path: str,
    api_key: Optional[str] = Header(None, alias=API_KEY_HEADER),
):
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    async def event_generator():
        await mcp_server.handle_connection(
            read_stream=sys.stdin,
            write_stream=sys.stdout,
        )

    return EventSourceResponse(event_generator())


@app.post("/mcp/{path:path}")
async def mcp_sse_post(
    path: str,
    api_key: Optional[str] = Header(None, alias=API_KEY_HEADER),
):
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    async def event_generator():
        await mcp_server.handle_connection(
            read_stream=sys.stdin,
            write_stream=sys.stdout,
        )

    return EventSourceResponse(event_generator())


@app.get("/tools")
async def list_mcp_tools(api_key: Optional[str] = Header(None, alias=API_KEY_HEADER)):
    if not verify_api_key(api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return {"tools": await list_tools()}


@app.get("/")
async def root(api_key: Optional[str] = Header(None, alias=API_KEY_HEADER)):
    auth_status = "authenticated" if verify_api_key(api_key) else "unauthenticated"
    return {
        "service": "Sentinel Prime MCP Server",
        "status": "running",
        "auth": auth_status,
        "endpoints": {
            "mcp": "/mcp/{path}",
            "tools": "/tools",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MCP_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
