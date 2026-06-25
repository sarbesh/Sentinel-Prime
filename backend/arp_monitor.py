import asyncio
import logging
import subprocess
import ipaddress
import re
from datetime import datetime
from typing import Dict, List, Optional

from sqlmodel import Session, select, or_

from database import engine, get_session
from models import Device, DeviceStatus
from api.sse import broadcast_device

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ARPWatcher:
    def __init__(self, network: str = "192.168.1.0/24"):
        self.network = network
        self.known_devices: Dict[str, dict] = {}
        self.running = False
        self.scan_interval = 30

    def get_arp_table(self) -> Dict[str, str]:
        """Get ARP table from the system."""
        arp_table = {}
        try:
            result = subprocess.run(
                ["arp", "-a"],
                capture_output=True,
                text=True,
                timeout=30
            )
            for line in result.stdout.splitlines():
                match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)\s+at\s+([0-9a-fA-F:]+)', line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).upper()
                    arp_table[ip] = mac
        except Exception as e:
            logger.error(f"Error getting ARP table: {e}")
        
        try:
            result = subprocess.run(
                ["ip", "neigh", "show"],
                capture_output=True,
                text=True,
                timeout=30
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    ip = parts[0]
                    if "lladdr" in line:
                        idx = parts.index("lladdr")
                        if idx + 1 < len(parts):
                            mac = parts[idx + 1].upper()
                            arp_table[ip] = mac
        except Exception as e:
            logger.error(f"Error getting ip neigh: {e}")
        
        return arp_table

    def ping_sweep(self, network: str) -> List[str]:
        """Ping sweep the network to populate ARP table."""
        active_hosts = []
        try:
            net = ipaddress.ip_network(network, strict=False)
            logger.info(f"Pinging network {network} ({net.num_addresses} addresses)")
            
            batch_size = 50
            addresses = list(net.hosts())
            
            for i in range(0, len(addresses), batch_size):
                batch = addresses[i:i + batch_size]
                args = ["ping", "-c", "1", "-W", "1"] + [str(a) for a in batch]
                result = subprocess.run(
                    args,
                    capture_output=True,
                    timeout=10
                )
                
                for addr in batch:
                    addr_str = str(addr)
                    response = subprocess.run(
                        ["ping", "-c", "1", "-W", "1", addr_str],
                        capture_output=True,
                        timeout=2
                    )
                    if response.returncode == 0:
                        active_hosts.append(addr_str)
                        
        except Exception as e:
            logger.error(f"Error in ping sweep: {e}")
        
        return active_hosts

    def scan_network(self) -> Dict[str, str]:
        """Scan network and return ARP table with MAC addresses."""
        logger.info("Starting network scan for ARP...")
        
        self.ping_sweep(self.network)
        
        arp_table = self.get_arp_table()
        logger.info(f"Found {len(arp_table)} devices in ARP table")
        
        return arp_table

    def update_devices_in_db(self, arp_table: Dict[str, str]):
        """Update device status in database based on ARP table."""
        session = Session(engine)
        
        try:
            current_ips = set(arp_table.keys())
            
            all_devices = session.exec(select(Device)).all()
            known_ips = {d.ip_address for d in all_devices}
            
            new_ips = current_ips - known_ips
            gone_ips = known_ips - current_ips
            
            for ip in new_ips:
                mac = arp_table.get(ip)
                if mac and mac != "00:00:00:00:00:00":
                    device = Device(
                        name=self._guess_device_name(mac),
                        ip_address=ip,
                        mac_address=mac,
                        status=DeviceStatus.ONLINE,
                        last_seen=datetime.utcnow(),
                    )
                    session.add(device)
                    session.commit()
                    session.refresh(device)
                    logger.info(f"New device detected: {ip} ({mac})")
                    broadcast_device({
                        "id": device.id,
                        "ip_address": ip,
                        "mac_address": mac,
                        "status": "online",
                        "event": "new",
                    })
            
            for ip in gone_ips:
                device = session.exec(
                    select(Device).where(Device.ip_address == ip)
                ).first()
                if device:
                    device.status = DeviceStatus.OFFLINE
                    device.last_seen = datetime.utcnow()
                    session.commit()
                    logger.info(f"Device went offline: {ip}")
                    broadcast_device({
                        "id": device.id,
                        "ip_address": ip,
                        "status": "offline",
                        "event": "offline",
                    })
            
            for ip, mac in arp_table.items():
                device = session.exec(
                    select(Device).where(Device.ip_address == ip)
                ).first()
                if device:
                    device.last_seen = datetime.utcnow()
                    if device.status != DeviceStatus.ONLINE:
                        device.status = DeviceStatus.ONLINE
                        session.commit()
                        broadcast_device({
                            "id": device.id,
                            "ip_address": ip,
                            "status": "online",
                            "event": "reconnected",
                        })
            
        except Exception as e:
            logger.error(f"Error updating devices: {e}")
            session.rollback()
        finally:
            session.close()

    def _guess_device_name(self, mac: str) -> str:
        """Try to guess device type from MAC address OUI."""
        oui = mac.replace(":", "").upper()[:6]
        
        vendor_guesses = {
            "A4:77": "Apple Device",
            "B4:2E": "Apple Device",
            "F0:18": "Apple Device",
            "00:1A": "Cisco",
            "00:1B": "Cisco",
            "00:25": "Cisco",
            "DC:A6": "Raspberry Pi",
            "B8:27": "Raspberry Pi",
            "E4:5F": "Raspberry Pi",
            "00:0C": "VMware",
            "00:50": "VMware",
            "08:00": "Intel",
            "3C:D9": "HP",
            "00:17": "HP",
            "00:1C": "HP",
            "00:21": "Samsung",
            "00:1D": "Samsung",
            "00:24": "Samsung",
            "00:26": "Samsung",
            "AC:DE": "OnePlus",
            "38:A4": "OnePlus",
            "00:1A": "Xiaomi",
            "34:80": "Xiaomi",
            "64:09": "Xiaomi",
            "28:6C": "Xiaomi",
            "64:B4": "Xiaomi",
            "00:0D": "Dell",
            "00:14": "Dell",
            "18:03": "Dell",
            "18:A9": "Dell",
            "00:16": "Dell",
            "00:1C": "Dell",
            "00:50": "Dell",
            "00:1E": "Dell",
            "00:21": "Dell",
            "28:C6": "Dell",
            "34:E6": "Dell",
            "00:24": "Dell",
            "00:22": "Dell",
            "00:26": "Dell",
            "00:1A": "Dell",
            "00:1B": "Dell",
            "00:1C": "Dell",
            "00:21": "Dell",
            "00:20": "Dell",
            "00:19": "Dell",
            "00:1B": "Dell",
            "00:1D": "Dell",
            "00:1F": "Dell",
            "00:21": "Dell",
        }
        
        vendor = vendor_guesses.get(oui, "Unknown Device")
        return f"{vendor} ({mac[-8:]})"

    async def monitor(self):
        """Main monitoring loop."""
        self.running = True
        
        logger.info(f"Starting ARP monitor for network {self.network}")
        
        while self.running:
            try:
                arp_table = self.scan_network()
                self.update_devices_in_db(arp_table)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
            
            await asyncio.sleep(self.scan_interval)
    
    def stop(self):
        """Stop the monitoring."""
        self.running = False
        logger.info("ARP monitor stopped")

arp_watcher: Optional[ARPWatcher] = None

def get_arp_watcher(network: str = "192.168.1.0/24") -> ARPWatcher:
    global arp_watcher
    if arp_watcher is None:
        arp_watcher = ARPWatcher(network)
    return arp_watcher

def start_arp_monitoring(network: str = "192.168.1.0/24"):
    """Start ARP monitoring in background."""
    import threading
    watcher = get_arp_watcher(network)
    
    def run_monitor():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(watcher.monitor())
    
    thread = threading.Thread(target=run_monitor, daemon=True)
    thread.start()
    logger.info("ARP monitoring started in background")
    return thread

def scan_and_update_devices():
    """One-time scan and update devices."""
    watcher = get_arp_watcher()
    arp_table = watcher.scan_network()
    watcher.update_devices_in_db(arp_table)
    return arp_table
