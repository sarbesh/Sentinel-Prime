#!/usr/bin/env python3
"""Initialize the Sentinel Prime database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from database import init_db
from models import Device, Scan, Alert, HoneypotEvent, ThreatIntel, NetworkInterface


def main():
    """Create all database tables."""
    print("Initializing Sentinel Prime database...")
    init_db()
    print("Database initialized successfully!")


if __name__ == "__main__":
    main()
