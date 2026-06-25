#!/usr/bin/env python3
"""
Sentinel Prime Core Orchestrator (sentinel-core)
Universal network security appliance orchestrator for IoT botnet detection.
Designed to run on any hardware: x86 servers, Raspberry Pi, embedded routers, etc.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Configuration paths
CORE_DIR = Path(__file__).parent
PROFILES_DIR = CORE_DIR / "profiles"
SERVICES_DIR = CORE_DIR / "services"
CONFIG_DIR = CORE_DIR / "config"

# Hardware profiles (can be extended)
HARDWARE_PROFILES = {
    "small": {
        "name": "Small (Router/Low-End IoT)",
        "min_ram_mb": 256,
        "max_concurrent_scans": 5,
        "eBPF_mode": "light",
        "suricata_threads": 1
    },
    "medium": {
        "name": "Medium (Raspberry Pi 4/5, Mini PC)",
        "min_ram_mb": 1024,
        "max_concurrent_scans": 20,
        "eBPF_mode": "standard",
        "suricata_threads": 2
    },
    "large": {
        "name": "Large (x86 Server/Desktop)",
        "min_ram_mb": 4096,
        "max_concurrent_scans": 100,
        "eBPF_mode": "full",
        "suricata_threads": 4
    }
}

def get_hardware_profile() -> str:
    """Detect system hardware and return appropriate profile name."""
    # Get RAM in MB
    try:
        with open("/proc/meminfo", "r") as f:
            mem_line = f.readline()
            mem_kb = int(mem_line.split()[1])
            ram_mb = mem_kb // 1024
    except Exception:
        ram_mb = 0

    # Fallback to psutil if proc fails
    if ram_mb == 0:
        try:
            import psutil
            ram_mb = psutil.virtual_memory().total // (1024 * 1024)
        except ImportError:
            ram_mb = 2048  # Default assumption

    # Determine profile
    if ram_mb < 512:
        return "small"
    elif ram_mb < 2048:
        return "medium"
    else:
        return "large"

def detect_kernel_version() -> tuple[int, int, int]:
    """Detect Linux kernel version for eBPF compatibility."""
    try:
        with open("/proc/version_signature", "r") as f:
            pass  # Not used
    except FileNotFoundError:
        pass

    # Try uname
    try:
        uname_out = subprocess.check_output(["uname", "-r"]).decode().strip()
        parts = uname_out.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except Exception:
        return (5, 4, 0)  # Assume modern enough

def check_tools() -> dict[str, bool]:
    """Check if required tools are available."""
    required_tools = {
        "nmap": "Network scanner",
        "suricata": "IDS/IPS engine",
        "python3": "Orchestrator runtime"
    }
    results = {}
    for tool, desc in required_tools.items():
        path = shutil.which(tool)
        if path:
            results[tool] = True
        else:
            results[tool] = False
    return results

def cmd_setup():
    """Setup command: detect hardware, prepare configuration."""
    print("🔍 Sentinel Prime Setup")
    print("-" * 40)

    # Hardware detection
    ram_mb = 0
    try:
        with open("/proc/meminfo", "r") as f:
            mem_line = f.readline()
            ram_mb = int(mem_line.split()[1]) // 1024
    except Exception:
        try:
            import psutil
            ram_mb = psutil.virtual_memory().total // (1024 * 1024)
        except ImportError:
            ram_mb = 2048

    kernel_version = detect_kernel_version()
    kernel_str = f"{kernel_version[0]}.{kernel_version[1]}.{kernel_version[2]}"

    profile_name = get_hardware_profile()
    profile = HARDWARE_PROFILES[profile_name]

    print(f"Hardware Detected:")
    print(f"  RAM: {ram_mb} MB")
    print(f"  Kernel: {kernel_str}")
    print(f"  Profile: {profile['name']} (auto-selected)")
    print()

    tools_status = check_tools()
    print("Required Tools:")
    for tool, status in tools_status.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {tool}")

    missing_tools = [t for t, s in tools_status.items() if not s]
    if missing_tools:
        print()
        print("⚠️  Missing tools. Install with:")
        if "nmap" in missing_tools:
            print("   sudo apt install nmap")
        if "suricata" in missing_tools:
            print("   sudo apt install suricata")

    print()
    print("Configuration Prepared:")
    print(f"  • eBPF mode: {profile['eBPF_mode']}")
    print(f"  • Suricata threads: {profile['suricata_threads']}")
    print(f"  • Max concurrent scans: {profile['max_concurrent_scans']}")

    return {
        "profile": profile_name,
        "ram_mb": ram_mb,
        "kernel": kernel_str,
        "tools": tools_status
    }

def cmd_status():
    """Status command: check health of services."""
    print("📊 Sentinel Prime Status")
    print("-" * 40)

    tools = check_tools()
    print("Tool Status:")
    for tool, installed in tools.items():
        icon = "✅ Running" if installed else "❌ Not Found"
        print(f"  {tool}: {icon}")

    print()

    # Try to check core services
    try:
        # Check if any Sentinel Prime containers/services running (for Docker mode)
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n") if result.stdout else []
            sentinel_services = [l for l in lines if "sentinel" in l.lower()]
            if sentinel_services:
                print("Detected Services:")
                for svc in sentinel_services:
                    print(f"  🟢 {svc}")
            else:
                print("No Sentinel Prime services running (check Docker or start manually)")
    except Exception:
        print("Docker not available - using native mode")

    print()
    profile = get_hardware_profile()
    print(f"Active Profile: {profile}")

def cmd_monitor():
    """Monitor command: start packet capture and analysis."""
    print("📡 Starting Sentinel Prime Monitor...")
    
    profile = get_hardware_profile()
    kernel_version = detect_kernel_version()
    
    # Determine capture method
    use_ebpf = kernel_version >= (5, 4, 0)
    
    print(f"Active Profile: {profile}")
    print(f"Kernel Version: {kernel_version[0]}.{kernel_version[1]}.{kernel_version[2]}")
    print(f"Capture Method: {'eBPF' if use_ebpf else 'AF_PACKET'}")
    print()
    
    # Check for required dependencies
    try:
        from bcc import BPF
        ebpf_available = True
    except ImportError:
        ebpf_available = False
    
    if use_ebpf and not ebpf_available:
        print("⚠️  eBPF requested but BCC library not installed.")
        print("   Install with: sudo apt install bpfcc-tools python3-bcc")
        print("   Falling back to AF_PACKET mode...")
        use_ebpf = False
    
    print("Starting flow collector...")
    print("(Press Ctrl+C to stop)")
    print()
    
    # Import and run collector
    import sys
    sys.path.insert(0, str(CORE_DIR / 'ebpf'))
    
    from flow_collector import run_collector
    
    # Determine interface (try common names)
    interfaces = ['eth0', 'enp0s3', 'wlan0', 'docker0']
    interface = 'eth0'  # Default
    
    try:
        run_collector(interface, use_ebpf)
    except KeyboardInterrupt:
        print("\n⏹️  Monitor stopped by user")

def main():
    parser = argparse.ArgumentParser(
        description="Sentinel Prime - Universal Network Security Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # setup subcommand
    setup_parser = subparsers.add_parser("setup", help="Setup hardware and configuration")
    
    # status subcommand
    status_parser = subparsers.add_parser("status", help="Check system and service status")

    # monitor subcommand
    monitor_parser = subparsers.add_parser("monitor", help="Start monitoring mode")

    args = parser.parse_args()

    if args.command == "setup":
        cmd_setup()
    elif args.command == "status":
        cmd_status()
    elif args.command == "monitor":
        cmd_monitor()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()