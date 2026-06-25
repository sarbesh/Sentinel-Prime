#!/usr/bin/env python3
import json
import os
import time
import requests
from pathlib import Path
from datetime import datetime

API_URL = os.environ.get("API_URL", "http://localhost:8000")
LOG_PATH = "/var/log/opencanary/honeypot.log"
CHECK_INTERVAL = 5

last_position = 0

SERVICE_PORT_MAP = {
    "ftp": 21,
    "ssh": 22,
    "telnet": 23,
    "http": 80,
    "https": 443,
    "smb": 445,
    "mysql": 3306,
    "postgresql": 5432,
    "httpproxy": 3128,
    "httphtmltitle": 8888,
    "git": 9418,
}


def send_event_to_backend(event_data):
    try:
        endpoint = f"{API_URL}/honeypot/events"
        response = requests.post(endpoint, json=event_data, timeout=10)
        if response.status_code in (200, 201):
            print(f"Event sent: {event_data.get('honeypot_type')} - {event_data.get('source_ip')}")
        else:
            print(f"Failed to send event: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending event: {e}")


def parse_log_line(line):
    try:
        data = json.loads(line.strip())
        
        honeypot_type = data.get("honeypot", data.get("type", "unknown")).lower()
        
        src_ip = data.get("src_host", data.get("src_ip", data.get("remoteHost", "")))
        dst_ip = data.get("local_host", data.get("dst_ip", ""))
        
        src_port = data.get("src_port", data.get("remotePort"))
        dst_port = SERVICE_PORT_MAP.get(honeypot_type, data.get("localPort", 0))
        
        protocol = data.get("proto", "").upper()
        
        details = data.get("banner", data.get("logdata", ""))
        if isinstance(details, dict):
            details = str(details)
        
        session = data.get("session", "")
        
        if src_ip and dst_ip:
            return {
                "honeypot_type": honeypot_type,
                "source_ip": src_ip,
                "source_port": src_port,
                "destination_ip": dst_ip,
                "destination_port": dst_port,
                "protocol": protocol,
                "service": honeypot_type,
                "timestamp": data.get("timestamp", datetime.utcnow().isoformat()),
                "details": details,
                "raw_log": json.dumps(data),
            }
    except json.JSONDecodeError:
        pass
    return None


def process_log():
    global last_position
    try:
        log_path = Path(LOG_PATH)
        if not log_path.exists():
            return

        current_size = log_path.stat().st_size

        if current_size < last_position:
            last_position = 0

        if current_size > last_position:
            with open(log_path, 'r') as f:
                f.seek(last_position)
                for line in f:
                    if line.strip():
                        event_data = parse_log_line(line)
                        if event_data:
                            send_event_to_backend(event_data)

            last_position = f.tell()

    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error processing log: {e}")


def main():
    print(f"Starting honeypot event forwarder to {API_URL}")
    while True:
        process_log()
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
