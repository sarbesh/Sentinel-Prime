#!/usr/bin/env python3
"""
Sentinel Prime eBPF Flow Collector
Userspace daemon that receives flow data from eBPF program via PERF_EVENT_ARRAY
"""

import os
import sys
import time
import signal
import logging
import ctypes
import socket
import struct
from multiprocessing import Process, Value, Array
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

# Attempt to import bpf tools
try:
    from bcc import BPF
    BCC_AVAILABLE = True
except ImportError:
    BCC_AVAILABLE = False

# Fallback to AF_PACKET if eBPF not available
import select

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sentinel-ebpf')

# Flow key structure (must match C struct)
class FlowKey(ctypes.Structure):
    _fields_ = [
        ("src_ip", ctypes.c_uint32),
        ("dst_ip", ctypes.c_uint32),
        ("src_port", ctypes.c_uint16),
        ("dst_port", ctypes.c_uint16),
        ("protocol", ctypes.c_uint8),
        ("pad", ctypes.c_uint8),
    ]

    def to_tuple(self):
        return (
            socket.inet_ntoa(struct.pack('!I', self.src_ip)),
            socket.inet_ntoa(struct.pack('!I', self.dst_ip)),
            socket.ntohs(self.src_port),
            socket.ntohs(self.dst_port),
            self.protocol
        )

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

class FlowStats:
    def __init__(self, key: FlowKey):
        self.key = key
        self.packet_count = 0
        self.byte_count = 0
        self.first_seen = time.time()
        self.last_seen = time.time()
    
    def update(self, packet_size: int):
        self.packet_count += 1
        self.byte_count += packet_size
        self.last_seen = time.time()
    
    def to_dict(self) -> dict:
        src_ip, dst_ip, src_port, dst_port, protocol = self.key.to_tuple()
        return {
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_port': src_port,
            'dst_port': dst_port,
            'protocol': protocol,
            'packet_count': self.packet_count,
            'byte_count': self.byte_count,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'duration': self.last_seen - self.first_seen
        }

class EBPFCollector:
    """eBPF-based flow collector using BCC"""
    
    def __init__(self, interface: str = 'eth0'):
        self.interface = interface
        self.bpf = None
        self.flows: Dict[FlowKey, FlowStats] = {}
        self.running = Value('b', False)
        self.event_count = Value('i', 0)
    
    def start(self):
        if not BCC_AVAILABLE:
            logger.error("BCC library not available. Install with: pip install bcc")
            return False
        
        try:
            # Load eBPF program
            with open('/home/sarbesh/workspace/sentinel-prime/core/ebpf/packet_capture.c', 'r') as f:
                bpf_text = f.read()
            
            self.bpf = BPF(text=bpf_text)
            
            # Attach eBPF program to interface (TC ingress)
            self.bpf.attach_tc(self.interface, "ingress")
            logger.info(f"Attached eBPF program to {self.interface}")
            
            # Setup perf event callback
            self.bpf["events"].open_perf_buffer(self._handle_event)
            
            self.running.value = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load eBPF program: {e}")
            return False
    
    def _handle_event(self, cpu, data, size):
        """Callback for eBPF perf events"""
        try:
            key = FlowKey.from_buffer_copy(data)
            
            if key not in self.flows:
                self.flows[key] = FlowStats(key)
            
            # Note: In production, you'd get packet size from a separate map
            # For now, we'll estimate based on event
            self.flows[key].update(1500)  # Average packet size estimate
            
            self.event_count.value += 1
            
        except Exception as e:
            logger.error(f"Error processing event: {e}")
    
    def run(self):
        """Main event loop"""
        if not self.start():
            return
        
        logger.info("Starting eBPF flow collector...")
        
        while self.running.value:
            try:
                self.bpf.perf_buffer_poll(timeout=1000)
                
                # Periodically flush old flows
                self._flush_old_flows()
                
                # Export flows to sentinel-core
                if self.event_count.value > 0:
                    self._export_flows()
                    
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                logger.error(f"Error in event loop: {e}")
                time.sleep(1)
    
    def _flush_old_flows(self):
        """Remove flows that haven't been seen recently"""
        now = time.time()
        timeout = 30  # seconds
        keys_to_remove = []
        
        for key, stats in self.flows.items():
            if now - stats.last_seen > timeout:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.flows[key]
    
    def _export_flows(self):
        """Export aggregated flows to sentinel-core"""
        # In production, this would send to a message queue or API
        # For now, we'll just log summary
        if self.event_count.value % 100 == 0:
            logger.info(f"Collected {len(self.flows)} active flows, {self.event_count.value} events")
    
    def stop(self):
        """Stop the collector"""
        self.running.value = False
        if self.bpf:
            self.bpf.detach_tc(self.interface, "ingress")
        logger.info("eBPF collector stopped")

class AFPacketCollector:
    """Fallback packet collector using AF_PACKET for older kernels"""
    
    def __init__(self, interface: str = 'eth0'):
        self.interface = interface
        self.sock = None
        self.flows: Dict[FlowKey, FlowStats] = {}
        self.running = Value('b', False)
        self.packet_count = Value('i', 0)
    
    def start(self):
        try:
            # Create raw socket
            self.sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
            self.sock.bind((self.interface, 0))
            self.sock.setblocking(False)
            
            logger.info(f"AF_PACKET collector bound to {self.interface}")
            self.running.value = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to create AF_PACKET socket: {e}")
            return False
    
    def run(self):
        """Main packet capture loop"""
        if not self.start():
            return
        
        logger.info("Starting AF_PACKET flow collector...")
        
        while self.running.value:
            try:
                ready, _, _ = select.select([self.sock], [], [], 1.0)
                
                if ready:
                    packet, _ = self.sock.recvfrom(65535)
                    self._process_packet(packet)
                    self.packet_count.value += 1
                    
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                logger.error(f"Error capturing packet: {e}")
                time.sleep(0.1)
    
    def _process_packet(self, packet: bytes):
        """Extract flow information from raw packet"""
        if len(packet) < 14:  # Ethernet header
            return
        
        # Parse Ethernet header
        eth_header = packet[0:14]
        eth_type = struct.unpack('!H', eth_header[12:14])[0]
        
        # Only process IPv4
        if eth_type != 0x0800 or len(packet) < 34:
            return
        
        # Parse IP header
        ip_header = packet[14:34]
        version_ihl = ip_header[0]
        ihl = (version_ihl & 0x0F) * 4
        
        if len(packet) < 14 + ihl:
            return
        
        src_ip = socket.inet_ntoa(ip_header[12:16])
        dst_ip = socket.inet_ntoa(ip_header[16:20])
        protocol = ip_header[9]
        
        # Parse TCP/UDP header
        transport_start = 14 + ihl
        if protocol == 6 and len(packet) >= transport_start + 4:  # TCP
            src_port, dst_port = struct.unpack('!HH', packet[transport_start:transport_start+4])
        elif protocol == 17 and len(packet) >= transport_start + 4:  # UDP
            src_port, dst_port = struct.unpack('!HH', packet[transport_start:transport_start+4])
        elif protocol == 1 and len(packet) >= transport_start + 2:  # ICMP
            src_port = packet[transport_start]  # Type
            dst_port = packet[transport_start+1]  # Code
        else:
            return
        
        # Create flow key
        key_data = (
            struct.pack('!I', socket.inet_aton(src_ip)),
            struct.pack('!I', socket.inet_aton(dst_ip)),
            struct.pack('!H', src_port),
            struct.pack('!H', dst_port),
            struct.pack('!B', protocol),
            struct.pack('!B', 0)
        )
        
        # This is a simplified approach - in production, use proper ctypes
        # For now, just count packets
        self.flows[(src_ip, dst_ip, src_port, dst_port, protocol)] = \
            self.flows.get((src_ip, dst_ip, src_port, dst_port, protocol), 0) + 1
    
    def stop(self):
        """Stop the collector"""
        self.running.value = False
        if self.sock:
            self.sock.close()
        logger.info("AF_PACKET collector stopped")

def run_collector(interface: str = 'eth0', use_ebpf: bool = True):
    """Run the appropriate collector based on availability"""
    
    if use_ebpf and BCC_AVAILABLE:
        # Check kernel version
        with open('/proc/version', 'r') as f:
            version_line = f.readline()
            # Simple version check
            if 'Microsoft' in version_line or 'WSL' in version_line:
                logger.warning("WSL detected, eBPF may not work. Falling back to AF_PACKET.")
                collector = AFPacketCollector(interface)
            else:
                collector = EBPFCollector(interface)
    else:
        logger.warning("eBPF not available, using AF_PACKET fallback")
        collector = AFPacketCollector(interface)
    
    try:
        collector.run()
    except KeyboardInterrupt:
        print("\nShutting down collector...")
        collector.stop()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sentinel Prime Flow Collector')
    parser.add_argument('--interface', '-i', default='eth0', help='Network interface to monitor')
    parser.add_argument('--no-ebpf', action='store_true', help='Force use of AF_PACKET instead of eBPF')
    args = parser.parse_args()
    
    logger.info(f"Starting Sentinel Prime Flow Collector on {args.interface}")
    logger.info(f"eBPF available: {BCC_AVAILABLE}, Force AF_PACKET: {args.no_ebpf}")
    
    run_collector(args.interface, not args.no_ebpf)