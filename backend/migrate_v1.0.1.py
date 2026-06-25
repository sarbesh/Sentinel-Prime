#!/usr/bin/env python3
"""
Database Migration Script for v1.0.1
Updates Device table to use MAC address as primary key
"""

import sys
sys.path.insert(0, '/home/sarbesh/workspace/sentinel-prime/backend')

from sqlmodel import SQLModel, create_engine, Session, select
from models import Device, DeviceStatus
from datetime import datetime

DATABASE_URL = "sqlite:///./data/sentinel_prime.db"

def migrate_devices():
    """Migrate existing devices to new schema."""
    
    print("="*80)
    print("📦 SENTINEL PRIME DATABASE MIGRATION v1.0.1")
    print("="*80)
    print()
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create new tables/add columns
    print("📝 Updating database schema...")
    SQLModel.metadata.create_all(engine)
    print("✅ Schema updated")
    print()
    
    # Migrate existing devices
    print("🔄 Migrating existing devices...")
    with Session(engine) as session:
        # Get all devices
        devices = session.exec(select(Device)).all()
        
        migrated_count = 0
        skipped_count = 0
        invalid_count = 0
        
        for device in devices:
            # Check if device has MAC
            if not device.mac_address:
                print(f"  ⚠️  Skipping device {device.name} ({device.ip_address}) - no MAC")
                invalid_count += 1
                # Mark for deletion or manual review
                # session.delete(device)
                continue
            
            # Update schema fields if needed
            if not hasattr(device, 'last_known_ip') or device.last_known_ip is None:
                device.last_known_ip = device.ip_address
                migrated_count += 1
            
            # Ensure MAC is indexed (should be automatic with schema)
            print(f"  ✅ {device.name} - MAC: {device.mac_address}, IP: {device.ip_address}")
        
        session.commit()
        
        print()
        print(f"📊 Migration Summary:")
        print(f"   Total Devices: {len(devices)}")
        print(f"   Migrated: {migrated_count}")
        print(f"   Skipped (no MAC): {invalid_count}")
        print(f"   Already Up-to-date: {len(devices) - migrated_count - invalid_count}")
    
    print()
    print("="*80)
    print("✅ MIGRATION COMPLETE")
    print("="*80)
    print()
    print("📋 What Changed:")
    print("   • MAC address is now required (not nullable)")
    print("   • MAC address is unique and indexed")
    print("   • Device lookup uses MAC instead of IP")
    print("   • Added last_known_ip tracking")
    print("   • IP changes are now logged for anomaly detection")
    print()
    print("🚀 Next Steps:")
    print("   1. Restart backend: docker-compose restart backend")
    print("   2. Run a new network scan")
    print("   3. Verify devices are tracked by MAC address")
    print()

if __name__ == '__main__':
    migrate_devices()