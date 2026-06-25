#!/usr/bin/env python3
"""
Suricata EVE-JSON Log Parser and Alert Forwarder
Real-time parsing of Suricata EVE logs with forwarding to sentinel-core API.
Supports IoT botnet detection alerts (Mirai, Gafgyt, C2 patterns).
"""

import json
import os
import sys
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
from collections import deque

# Configuration
API_URL = os.environ.get("API_URL", "http://localhost:8000")
EVE_LOG_PATH = os.environ.get("EVE_LOG_PATH", "/var/log/suricata/eve.json")
CHECK_INTERVAL = float(os.environ.get("CHECK_INTERVAL", "2"))
ALERT_BUFFER_SIZE = int(os.environ.get("ALERT_BUFFER_SIZE", "100"))
ENABLE_DEDUP = os.environ.get("ENABLE_DEDUP", "true").lower() == "true"
DEDUP_WINDOW = int(os.environ.get("DEDUP_WINDOW", "60"))  # seconds

# IoT Botnet Signatures for priority handling
IOT_BOTNET_SIGNATURES = [
    "mirai", "gafgyt", "qbot", "okiru", "reaper", "ioshelper",
    "telnet exploit", "ssh exploit", "mallory", "hideandseek",
    "masscan", "device probe", "botnet", "c2", "command and control"
]


class AlertDeduplicator:
    """Deduplicates alerts within a time window to prevent flooding."""
    
    def __init__(self, window_seconds: int = 60):
        self.window = window_seconds
        self.seen: Dict[str, float] = {}
        self.cleanup_interval = 300
        self.last_cleanup = time.time()
    
    def is_duplicate(self, alert_key: str) -> bool:
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup()
        
        if alert_key in self.seen:
            if now - self.seen[alert_key] < self.window:
                return True
        self.seen[alert_key] = now
        return False
    
    def _cleanup(self):
        now = time.time()
        expired = [k for k, t in self.seen.items() if now - t > self.window]
        for k in expired:
            del self.seen[k]


class AlertBuffer:
    """Circular buffer for rate-limited alert forwarding."""
    
    def __init__(self, max_size: int = 100):
        self.buffer: deque = deque(maxlen=max_size)
        self.stats = {"total": 0, "forwarded": 0, "dropped": 0}
    
    def add(self, alert: Dict[str, Any]) -> bool:
        self.stats["total"] += 1
        max_size = self.buffer.maxlen or 100
        if len(self.buffer) >= max_size:
            self.stats["dropped"] += 1
            old = self.buffer.popleft()
        self.buffer.append(alert)
        self.stats["forwarded"] = len(self.buffer)
        return True
    
    def flush(self) -> List[Dict[str, Any]]:
        alerts = list(self.buffer)
        self.buffer.clear()
        return alerts
    
    def get_stats(self) -> Dict[str, int]:
        return self.stats.copy()


def generate_alert_key(alert: Dict[str, Any]) -> str:
    """Generate unique key for deduplication."""
    src_ip = alert.get("source_ip", "")
    dest_ip = alert.get("dest_ip", "")
    signature = alert.get("signature", "")
    timestamp = alert.get("timestamp", "")[:16]  # Minute precision
    return f"{src_ip}|{dest_ip}|{signature}|{timestamp}"


def classify_alert_severity(alert: Dict[str, Any]) -> str:
    """Classify alert severity based on signature and category."""
    signature = alert.get("signature", "").lower()
    category = alert.get("category", "").lower()
    
    # IoT Botnet signatures get critical severity
    for botnet in IOT_BOTNET_SIGNATURES:
        if botnet in signature or botnet in category:
            return "critical"
    
    # High severity for exploit attempts
    exploit_keywords = ["exploit", "injection", "rce", "privilege"]
    if any(kw in signature for kw in exploit_keywords):
        return "high"
    
    # Medium for scans and policy violations
    if category in ["network-scan", "policy-violation"]:
        return "medium"
    
    return "low"


def get_threat_intel_data(alert: Dict[str, Any]) -> Dict[str, Any]:
    """Attempt to enrich alert with threat intelligence."""
    threat_info = {}
    signature = alert.get("signature", "").lower()
    
    # Basic IOC extraction
    if "mirai" in signature:
        threat_info["threat_family"] = "Mirai"
        threat_info["threat_actor"] = "IoT Botnet"
        threat_info["ttp_id"] = "T1498"  # MITRE ATT&CK Network DoS
    elif "gafgyt" in signature:
        threat_info["threat_family"] = "Gafgyt"
        threat_info["threat_actor"] = "IoT Botnet"
        threat_info["ttp_id"] = "T1071"  # Application Layer Protocol
    elif "c2" in signature or "command" in signature:
        threat_info["threat_type"] = "C2 Communication"
        threat_info["ttp_id"] = "T1071"
    elif "telnet" in signature:
        threat_info["threat_type"] = "Telnet Exploitation"
        threat_info["ttp_id"] = "T1021.007"  # Remote Services: Telnet
    
    return threat_info


def send_alerts_to_backend(alerts: List[Dict[str, Any]], api_url: str) -> int:
    """Send batch of alerts to backend API."""
    if not alerts:
        return 0
    
    endpoint = f"{api_url}/alerts/ids-alerts"
    successful = 0
    
    try:
        response = requests.post(endpoint, json={"alerts": alerts}, timeout=10)
        if response.status_code in (200, 201):
            successful = len(alerts)
            print(f"[{datetime.now().isoformat()}] Sent {successful} alerts")
        else:
            print(f"[{datetime.now().isoformat()}] Failed: HTTP {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().isoformat()}] Backend unavailable (will retry)")
    except requests.exceptions.Timeout:
        print(f"[{datetime.now().isoformat()}] Request timeout")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] Error sending alerts: {e}")
    
    return successful


def parse_eve_event(line: str) -> Optional[Dict[str, Any]]:
    """Parse a single EVE-JSON event into normalized alert format."""
    try:
        event = json.loads(line.strip())
        
        # Only process alert events
        if event.get("event_type") != "alert":
            return None
        
        # Normalize alert structure
        alert_data = event.get("alert", {})
        flow_data = event.get("flow", {})
        
        normalized = {
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "source_ip": event.get("src_ip", ""),
            "source_port": event.get("src_port", 0),
            "dest_ip": event.get("dest_ip", ""),
            "dest_port": event.get("dest_port", 0),
            "protocol": event.get("proto", ""),
            "signature": alert_data.get("signature", ""),
            "signature_id": alert_data.get("signature_id", 0),
            "severity": alert_data.get("severity", 3),
            "category": alert_data.get("category", ""),
            "classification": alert_data.get("classification", ""),
            "gid": event.get("gid", 1),
            "rev": event.get("rev", 1),
            "flow_id": event.get("flow_id", 0),
            "tcp_flags": event.get("tcp_flags", ""),
            "bytes_to_server": flow_data.get("bytes_toserver", 0),
            "bytes_to_client": flow_data.get("bytes_toclient", 0),
            "raw_event": line.strip(),
        }
        
        # Add calculated fields
        normalized["severity_name"] = classify_alert_severity(normalized)
        normalized["threat_intel"] = get_threat_intel_data(normalized)
        normalized["direction"] = "inbound" if normalized["dest_ip"].startswith(("192.168.", "10.", "172.16.")) else "outbound"
        
        return normalized
        
    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"Error parsing event: {e}")
        return None


def process_eve_log(
    log_path: Path,
    position: int,
    buffer: AlertBuffer,
    deduplicator: Optional[AlertDeduplicator] = None
) -> int:
    """Process new lines from EVE log file."""
    if not log_path.exists():
        return position
    
    current_size = log_path.stat().st_size
    
    # Handle log rotation
    if current_size < position:
        print(f"Log rotation detected, resetting position")
        position = 0
    
    if current_size <= position:
        return position
    
    # Read new lines
    with open(log_path, 'r') as f:
        f.seek(position)
        for line in f:
            if not line.strip():
                continue
            
            alert = parse_eve_event(line)
            if alert is None:
                continue
            
            # Check for duplicates
            if deduplicator and ENABLE_DEDUP:
                alert_key = generate_alert_key(alert)
                if deduplicator.is_duplicate(alert_key):
                    continue
            
            buffer.add(alert)
        
        position = f.tell()
    
    return position


def monitor_stats(log_path: Path) -> Dict[str, Any]:
    """Gather monitoring statistics."""
    stats = {"log_exists": False, "log_size": 0}
    if log_path.exists():
        stats["log_exists"] = True
        stats["log_size"] = log_path.stat().st_size
    return stats


def main():
    """Main alert forwarder loop."""
    eve_path = Path(EVE_LOG_PATH)
    
    print(f"🔍 Sentinel Prime Suricata Alert Forwarder")
    print(f"   EVE Log Path: {eve_path}")
    print(f"   API Endpoint: {API_URL}")
    print(f"   Dedup Window: {DEDUP_WINDOW}s (enabled: {ENABLE_DEDUP})")
    print(f"   Buffer Size: {ALERT_BUFFER_SIZE}")
    print(f"   Poll Interval: {CHECK_INTERVAL}s")
    print("-" * 60)
    
    buffer = AlertBuffer(ALERT_BUFFER_SIZE)
    deduplicator = AlertDeduplicator(DEDUP_WINDOW) if ENABLE_DEDUP else None
    last_position = 0
    
    # Wait for log file to exist
    if not eve_path.exists():
        print(f"Waiting for EVE log file at {eve_path}...")
        for i in range(30):
            time.sleep(1)
            if eve_path.exists():
                print(f"Log file found after {i+1}s")
                break
        else:
            print("Log file not found, starting anyway...")
    
    # Main processing loop
    batch_interval = 5
    batch_counter = 0
    
    while True:
        try:
            # Process new log entries
            last_position = process_eve_log(
                eve_path, last_position, buffer, deduplicator
            )
            
            # Periodic stats
            if batch_counter % 10 == 0:
                stats = buffer.get_stats()
                mon = monitor_stats(eve_path)
                print(f"[{datetime.now().isoformat()}] Stats: "
                      f"processed={stats['total']}, "
                      f"forwarded={stats['forwarded']}, "
                      f"dropped={stats['dropped']}, "
                      f"log_size={mon['log_size']}")
            
            # Flush buffer periodically
            batch_counter += 1
            if batch_counter >= batch_interval:
                batch_counter = 0
                alerts = buffer.flush()
                if alerts:
                    send_alerts_to_backend(alerts, API_URL)
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\nShutting down alert forwarder...")
            # Flush remaining alerts
            remaining = buffer.flush()
            if remaining:
                send_alerts_to_backend(remaining, API_URL)
            sys.exit(0)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()