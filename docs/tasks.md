# Task/TODO List

## How To Use
- Each task is modular and linked to its module's README and docs.
- Anyone (human or AI) can pick up any task—just read the described files and get started.
- If details are missing, update the documentation as part of the task!

---

### Project Bootstrapping
- [x] Create project structure, LICENSE, README, docs
- [x] Write architecture diagram and ADRs
- [x] Add per-module README files

### Web & Mobile Unified UI (React Native)
- [ ] Scaffold React Native codebase under `/web-ui`
- [ ] Login/auth system
- [ ] Dashboard, report, and config screens

### Backend/API
- [ ] Scaffold basic backend API in `/backend`
- [ ] Database setup/migration scripts
- [ ] API endpoints for modules

### Network Scanner
- [ ] Scaffold Nmap/OpenVAS container in `/network-scanner`
- [ ] UI and API integration (scan results)

### Device Monitor
- [ ] DHCP listener trigger in `/new-device-monitor`
- [ ] Scan-on-connect scripts

### IPS/IDS
- [ ] Scaffold Suricata/Zeek container in `/ips-ids`
- [ ] Alerts to UI/API

### Honeypot
- [ ] Scaffold OpenCanary/Dionaea in `/honeypot`
- [ ] Attack logging, UI/API integration

### Threat Intelligence
- [ ] Feed-updater script in `/threat-intel`
- [ ] Sync with Suricata/Zeek/honeypot rules

### Reporting
- [ ] HTML report generation script(s)
- [ ] Notification setup (UI, push, email)

### Documentation & Maintenance
- [x] Every module must have a README
- [x] ADRs describe key decisions
- [x] Docs updated regularly for clarity

---

> Find a task, check its module README and API, and get started. Update documentation as you work!
