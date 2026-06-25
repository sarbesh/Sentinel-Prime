# TASK: Threat Intelligence Feed Implementation

## Objective
Implement a system to automatically update the `threat_intel` table in the SENTINEL PRIME database from external threat feeds.

## Requirements
1. **Feed Integration**: Create scripts to pull data from:
   - AlienVault OTX
   - Abuse.ch (URLHaus, SSLBL)
   - VirusTotal (if API key available) or other open feeds.
2. **Data Normalization**: Map external feed data to the `ThreatIntel` model in `backend/models.py`.
3. **Database Update**: Use the backend API or direct DB connection to populate the `threat_intel` table.
4. **Scheduling**: Ensure the updater can be run periodically (e.g., via cron or as a background service).

## Deliverables
- Python scripts for feed pulling.
- Documentation on how to configure API keys.
- Verification that indicators are appearing in the database.
