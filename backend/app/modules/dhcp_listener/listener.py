from sqlalchemy import func
import asyncio
import logging
from scapy.all import *
from app.core.database import SessionLocal
from app.models import Device
from app.core.config import settings

logger = logging.getLogger(__name__)

class DHCPListener:
    def __init__(self):
        self.interface = settings.DHCP_LISTENER_INTERFACE
        self.port = settings.DHCP_LISTENER_PORT
        self.running = False

    async def start_listener(self):
        """Start the DHCP listener in a background task."""
        self.running = True
        logger.info(f"Starting DHCP listener on interface {self.interface}, port {self.port}")
        # Run the sniffing in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self._sniff_dhcp)

    def stop_listener(self):
        self.running = False

    def _sniff_dhcp(self):
        """Sniff for DHCP packets (port 67 and 68)."""
        # Filter for DHCP packets (server port 67, client port 68)
        filter_str = f"udp and (port {self.port} or port 68)"
        sniff(iface=self.interface, filter=filter_str, prn=self._handle_dhcp_packet, store=0, stop_filter=lambda x: not self.running)

    def _handle_dhcp_packet(self, packet):
        """Handle a captured DHCP packet."""
        if DHCP in packet:
            # Extract MAC address from the packet
            mac = packet[Ether].src
            # Check if we already know this device
            db = SessionLocal()
            try:
                device = db.query(Device).filter(Device.mac_address == mac).first()
                if not device:
                    logger.info(f"New device detected: {mac}")
                    # Extract IP address if available (from BOOTP layer)
                    ip = None
                    if BOOTP in packet:
                        ip = packet[BOOTP].yiaddr  # Your IP address
                    # Extract hostname if available (from DHCP options)
                    hostname = None
                    vendor = None
                    if DHCP in packet:
                        for option in packet[DHCP].options:
                            if option[0] == 'hostname':
                                hostname = option[1].decode('utf-8') if isinstance(option[1], bytes) else option[1]
                            elif option[0] == 'vendor_class_id':
                                vendor = option[1].decode('utf-8') if isinstance(option[1], bytes) else option[1]
                    # Create new device record
                    new_device = Device(
                        mac_address=mac,
                        ip_address=ip,
                        hostname=hostname,
                        vendor=vendor
                    )
                    db.add(new_device)
                    db.commit()
                    logger.info(f"Added new device: {mac} with IP {ip}")
                    # TODO: Trigger a scan for this device (e.g., run nmap scan)
                    # For now, we just log that we would trigger a scan.
                    logger.info(f"Would trigger a scan for device {mac}")
                else:
                    # Update last seen
                    device.last_seen = func.now()
                    db.commit()
            except Exception as e:
                logger.error(f"Error handling DHCP packet: {e}")
                db.rollback()
            finally:
                db.close()

# Global listener instance
listener = DHCPListener()