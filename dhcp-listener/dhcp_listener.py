#!/usr/bin/env python3
"""
DHCP Listener for SENTINEL PRIME
Listens for DHCP requests and triggers network scans for new devices.
"""

import os
import time
import logging
from scapy.all import *
import requests
import json

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
INTERFACE = os.getenv("INTERFACE", "eth0")  # Default interface, can be overridden
DHCP_PORT_SERVER = 67  # DHCP server port
DHCP_PORT_CLIENT = 68  # DHCP client port
CHECK_INTERVAL = 5  # Seconds between duplicate checks (not used in packet sniffing, but for logic)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cache of seen MAC addresses to avoid duplicate processing
seen_macs = set()

def extract_dhcp_options(packet):
    """Extract DHCP options from a packet."""
    options = {}
    if DHCP in packet:
        for option in packet[DHCP].options:
            if isinstance(option, tuple):
                key, value = option
                options[key] = value
            elif option == 'end':
                break
    return options

def get_hostname_from_options(options):
    """Extract hostname from DHCP options."""
    # Hostname is option 12
    if 12 in options:
        return options[12].decode('utf-8') if isinstance(options[12], bytes) else options[12]
    return None

def get_requested_ip_from_options(options):
    """Extract requested IP address from DHCP options."""
    # Requested IP is option 50
    if 50 in options:
        return options[50]
    return None

def process_dhcp_packet(packet):
    """Process a DHCP packet to extract device information."""
    try:
        # Check if this is a DHCP packet
        if not packet.haslayer(DHCP):
            return

        # Get MAC address from Ethernet layer
        if packet.haslayer(Ether):
            mac = packet[Ether].src.upper()
        else:
            # If no Ethernet layer, skip (shouldn't happen on Ethernet networks)
            return

        # Skip if we've already seen this MAC recently
        if mac in seen_macs:
            return

        # Get DHCP options
        options = extract_dhcp_options(packet)
        
        # Get hostname
        hostname = get_hostname_from_options(options)
        
        # Get requested IP address (from option 50)
        requested_ip = get_requested_ip_from_options(options)
        
        # If no requested IP, try to get from the 'yiaddr' field (your IP address) in the IP layer
        # This is more common in DHCP Offer (from server) but we are listening for client requests.
        # In DHCP Request (from client), the yiaddr is usually 0.0.0.0 or the IP they are requesting.
        # We'll use the yiaddr if requested_ip is not set.
        ip_address = requested_ip
        if not ip_address and packet.haslayer(IP):
            yiaddr = packet[IP].yiaddr
            if yiaddr != "0.0.0.0":
                ip_address = yiaddr

        # If we still don't have an IP, we cannot proceed with a scan (but we can still register the device)
        if not ip_address:
            logger.warning(f"DHCP packet from {mac} has no IP address. Skipping scan trigger.")
            # We might still want to register the device without an IP? The backend might require IP.
            # For now, we skip if no IP.
            return

        logger.info(f"Detected new device via DHCP: MAC={mac}, IP={ip_address}, Hostname={hostname}")

        # Add to seen MACs to prevent immediate duplicates
        seen_macs.add(mac)
        # We'll remove it after a while to allow re-detection after a long time (optional)
        # For simplicity, we'll keep it for the duration of the container run.

        # Step 1: Create device via backend API
        device_data = {
            "mac_address": mac,
            "ip_address": ip_address,
            "hostname": hostname if hostname else f"unknown-{mac[-8:]}",
            "status": "online",
            "type": "unknown"  # Will be updated by scanner/OS detection
        }

        try:
            device_response = requests.post(
                f"{BACKEND_URL}/devices/",
                json=device_data,
                timeout=10
            )
            device_response.raise_for_status()
            device = device_response.json()
            logger.info(f"Created device via API: {device.get('id')}")
        except Exception as e:
            logger.error(f"Failed to create device via API: {e}")
            return

        # Step 2: Trigger a network scan for this device
        scan_data = {
            "target": ip_address,
            "scan_type": "quick",  # Use quick scan for new device detection
            "ports": ""  # Let the scanner decide default ports
        }

        try:
            scan_response = requests.post(
                f"{BACKEND_URL}/scans/network",
                json=scan_data,
                timeout=10
            )
            scan_response.raise_for_status()
            scan_result = scan_response.json()
            logger.info(f"Triggered network scan for {ip_address}: {scan_result.get('id')}")
        except Exception as e:
            logger.error(f"Failed to trigger network scan for {ip_address}: {e}")

    except Exception as e:
        logger.error(f"Error processing DHCP packet: {e}")

def start_dhcp_listener(interface=INTERFACE):
    """Start listening for DHCP packets on the specified interface."""
    logger.info(f"Starting DHCP listener on interface {interface}")
    logger.info(f"Filter: udp and (port {DHCP_PORT_SERVER} or port {DHCP_PORT_CLIENT})")
    
    # BPF filter for DHCP packets (client and server ports)
    bpf_filter = f"udp and (port {DHCP_PORT_SERVER} or port {DHCP_PORT_CLIENT})"
    
    # Start sniffing
    sniff(
        iface=interface,
        filter=bpf_filter,
        prn=process_dhcp_packet,
        store=0  # Don't store packets to save memory
    )

if __name__ == "__main__":
    # Allow interface to be overridden by environment variable
    interface = os.getenv("INTERFACE", "eth0")
    start_dhcp_listener(interface)