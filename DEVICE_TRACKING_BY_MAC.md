# 📚 Device Tracking by MAC Address - Technical Documentation

**Version**: v1.0.1+  
**Date**: June 25, 2026  
**Impact**: Breaking change for device management  

---

## 🎯 Overview

Starting in v1.0.1, Sentinel Prime tracks devices by their **MAC address** instead of IP address. This fundamental change improves device tracking accuracy and enables detection of suspicious IP changes.

### Why MAC-Based Tracking?

| Aspect | IP-Based (Old) | MAC-Based (New) |
|--------|----------------|-----------------|
| **Uniqueness** | ❌ IPs can change (DHCP) | ✅ MAC is permanent |
| **Device Identity** | ❌ Same IP = same "device" | ✅ Same MAC = same device |
| **IP Changes** | ❌ Lost on DHCP renew | ✅ Tracked and logged |
| **Duplicate IPs** | ❌ Confusion | ✅ Easily detected |
| **Anomaly Detection** | ❌ Limited | ✅ IP changes tracked |

---

## 🗃️ Database Schema Changes

### Old Schema (Pre-v1.0.1)
```python
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ip_address: str  # Required
    mac_address: Optional[str] = None  # Optional!
    # ... other fields
```

**Problems**:
- Devices could exist without MAC (47 invalid devices in beta!)
- Lookups were by IP (which changes)
- No tracking of IP history

### New Schema (v1.0.1+)
```python
class Device(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    mac_address: str = Field(unique=True, index=True, nullable=False)  # Required & Unique!
    name: str
    ip_address: Optional[str] = None  # Changed to Optional
    last_known_ip: Optional[str] = None  # New field for tracking
    
    class Config:
        schema_extra = {
            "example": {
                "mac_address": "00:1A:2B:3C:4D:5E",
                "name": "My iPhone",
                "ip_address": "192.168.0.105",
                "os": "iOS 17"
            }
        }
```

**Improvements**:
- ✅ MAC address required (cannot be NULL)
- ✅ MAC address unique (no duplicates)
- ✅ MAC address indexed (fast lookups)
- ✅ IP tracked separately from identity
- ✅ `last_known_ip` for anomaly detection

---

## 🔄 Device Discovery Flow (New)

### Before (v1.0.0)
```
1. Scan detects host at 192.168.0.105
2. Lookup: SELECT * FROM devices WHERE ip_address = '192.168.0.105'
3. If not found: Create device with IP=192.168.0.105
4. Problem: No MAC validation!
```

### After (v1.0.1)
```
1. Scan detects host at 192.168.0.105 with MAC 00:1A:2B:3C:4D:5E
2. Lookup: SELECT * FROM devices WHERE mac_address = '00:1A:2B:3C:4D:5E'
3. If not found: Create device with MAC and IP
4. If exists: Update last_seen, check if IP changed
5. Log IP change for anomaly detection
```

### Code Example
```python
# Lookup by MAC (permanent identifier)
device = session.exec(
    select(Device).where(Device.mac_address == mac)
).first()

if not device:
    # New device - store MAC, IP, OS
    device = Device(
        name=hostname,
        ip_address=current_ip,
        mac_address=mac,
        last_known_ip=current_ip,  # Track it
        os=os_detection
    )
    session.add(device)
else:
    # Existing device - update status
    device.last_seen = datetime.utcnow()
    device.status = DeviceStatus.ONLINE
    
    # Check if IP changed
    if device.ip_address != current_ip:
        logger.info(f"Device {mac} IP changed: {device.ip_address} → {current_ip}")
        device.ip_address = current_ip
        device.last_known_ip = current_ip  # Update tracking
    
    # Update OS if newly detected
    if os_detection and not device.os:
        device.os = os_detection

session.commit()
```

---

## 🚨 Anomaly Detection - IP Changes

The new schema enables detection of suspicious activity:

### Normal DHCP Renewal
```
Day 1: 00:1A:2B:3C:4D:5E → 192.168.0.105
Day 2: 00:1A:2B:3C:4D:5E → 192.168.0.106 (DHCP lease expired)
✅ Normal behavior - logged but not alerted
```

### Suspicious IP Change (Potential Attack)
```
Device: 00:1A:2B:3C:4D:5E (iPhone)
Last IP: 192.168.0.105
Current IP: 192.168.0.105
⚠️ Same IP but different MAC detected = ARP spoofing!
```

### Spoofed MAC Detection
```
Known Device: iPhone (00:1A:2B:3C:4D:5E)
Scan detects: IP 192.168.0.105 with MAC DE:AD:BE:EF:CA:FE
⚠️ Two devices claiming same IP with different MACs
Alert: Potential MAC spoofing attack
```

---

## 📊 Querying Devices

### By MAC Address (Primary Method)
```python
# Get specific device by MAC
device = session.exec(
    select(Device).where(Device.mac_address == "00:1A:2B:3C:4D:5E")
).first()

# Get all devices from specific vendor (OUI lookup)
devices = session.exec(
    select(Device).where(Device.mac_address.startswith("00:1A:2B"))
).all()
```

### By IP Address (Secondary, for convenience)
```python
# Get device currently at IP
device = session.exec(
    select(Device).where(Device.ip_address == "192.168.0.105")
).first()

if device:
    print(f"Device: {device.name}, MAC: {device.mac_address}")
```

### Detect IP Changes
```python
from sqlalchemy import func

# Find devices that changed IP recently
ip_changes = session.exec(
    select(Device).where(
        Device.ip_address != Device.last_known_ip
    )
).all()

for device in ip_changes:
    print(f"{device.name}: {device.last_known_ip} → {device.ip_address}")
```

---

## 🛠️ Migration Guide

### For Existing Deployments

#### Option 1: Automatic Migration (Recommended)
```bash
# Run migration script
python3 backend/migrate_v1.0.1.py

# Restart backend
docker-compose restart backend

# Run new scan to populate data
curl -X POST http://localhost:8000/scans/network \
  -H "Content-Type: application/json" \
  -d '{"target": "192.168.0.1/24"}'
```

What the migration does:
1. ✅ Adds `mac_address` constraint (NOT NULL, UNIQUE)
2. ✅ Adds `last_known_ip` column
3. ✅ Removes devices without MAC addresses
4. ✅ Updates existing devices with MAC as primary lookup

#### Option 2: Fresh Install
```bash
# Clean database
rm data/sentinel_prime.db

# Restart services
docker-compose down && docker-compose up -d

# Run initial scan
python3 core/sentinel-core.py setup
```

---

## 🐛 Troubleshooting

### Issue: "Duplicate MAC address" Error
**Cause**: Two devices trying to use same MAC  
**Solution**: 
```sql
-- Find duplicate
SELECT mac_address, COUNT(*) FROM devices 
GROUP BY mac_address HAVING COUNT(*) > 1;

-- Delete duplicate (keep one)
DELETE FROM devices WHERE id = <duplicate_id>;
```

### Issue: Devices Not Showing in UI
**Cause**: Old devices without MAC addresses  
**Solution**:
```bash
# Check for invalid devices
sqlite3 data/sentinel_prime.db \
  "SELECT * FROM devices WHERE mac_address IS NULL;"

# Delete invalid devices
sqlite3 data/sentinel_prime.db \
  "DELETE FROM devices WHERE mac_address IS NULL;"
```

### Issue: IP Not Updating
**Cause**: Device lookup failing by MAC  
**Solution**:
```bash
# Verify MAC format (should be uppercase with colons)
sqlite3 data/sentinel_prime.db \
  "SELECT mac_address FROM devices LIMIT 5;"

# Correct format example: "00:1A:2B:3C:4D:5E"
# Incorrect: "00-1A-2B-3C-4D-5E" or "001A2B3C4D5E"
```

---

## 📈 Benefits Summary

### Data Quality
- ✅ **No Invalid Devices**: All devices have MAC addresses
- ✅ **Accurate Identity**: Device = MAC, not IP
- ✅ **No Duplicates**: Unique constraint prevents duplicates

### Security
- ✅ **IP Change Monitoring**: Track DHCP vs suspicious changes
- ✅ **Spoofing Detection**: Alert on MAC/IP conflicts
- ✅ **Historical Tracking**: Know where devices have been

### Performance
- ✅ **Faster Lookups**: MAC index is more efficient
- ✅ **Fewer Queries**: Single lookup by MAC
- ✅ **Better Caching**: Stable identifiers

### User Experience
- ✅ **Stable Device Names**: Doesn't change with IP
- ✅ **Accurate Device Count**: No duplicates
- ✅ **Better Alerts**: Know when IP changes are suspicious

---

## 🔮 Future Enhancements

### Planned Features (Phase 2.5)
1. **Device Naming**: Override auto-detected names
2. **MAC Vendor Lookup**: Identify manufacturer from OUI
3. **IP History Log**: Full history of IP assignments
4. **Device Profile**: Track typical IP ranges, OS versions
5. **Anomaly Scoring**: Alert on unusual IP/MAC behavior

### Example: MAC Vendor Lookup
```python
import requests

def get_vendor_from_mac(mac: str) -> str:
    """Lookup vendor from MAC OUI."""
    # MAC OUI is first 3 octets
    oui = mac.replace(':', '').upper()[:6]
    
    # Query MAC vendor database
    response = requests.get(
        f"https://api.macvendors.com/{oui}"
    )
    
    if response.status_code == 200:
        return response.text  # e.g., "Apple, Inc."
    return "Unknown"
```

---

**Status**: ✅ Live in v1.0.1+  
**Migration**: Automatic on first scan  
**Rollback**: Not recommended (would lose data quality)