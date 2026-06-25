# TASK: DHCP-to-Scan Trigger Implementation

## Objective
Enable automatic network scanning when a new device is detected by the DHCP listener.

## Requirements
1. **Event Detection**: Modify `dhcp-listener/dhcp_listener.py` to identify when a new MAC address requests an IP (DHCP Discover/Request).
2. **Backend Trigger**: When a new device is detected, call the backend API endpoint for initiating a scan (e.g., `POST /api/scans/`).
3. **Scan Configuration**: The scan should be a "Quick" scan targeting the newly assigned IP.
4. **Deduplication**: Ensure that the same device doesn't trigger multiple scans in a short window.

## Deliverables
- Updated `dhcp_listener.py`.
- Verification logs showing a new device detection triggering a backend scan.
- Updated `docker-compose.yml` if any new dependencies are added.
