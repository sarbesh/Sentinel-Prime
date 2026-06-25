# SENTINEL PRIME Roadmap

This document traces planned features, enhancements, and priorities for the project—each modular and independently achievable.

---
## Roadmap: Modules and Milestones

### 1. Project Setup
- [x] Initialize repo, LICENSE, README
- [x] Write base documentation and ADRs

### 2. Web & Mobile Unified UI
- [ ] React Native codebase scaffold
- [ ] Auth, dashboard, device config

### 3. Backend/API
- [ ] Scaffold API and DB
- [ ] Modular endpoints

### 4. Network Scanner
- [ ] Nmap/OpenVAS container, core logic
- [ ] UI/DB integration

### 5. New Device Monitor
- [ ] DHCP listener container
- [ ] Scan trigger on new device connect

### 6. IPS/IDS
- [ ] Suricata/Zeek integration
- [ ] Alert/report pipeline to UI

### 7. Honeypot
- [ ] OpenCanary/Dionaea integration
- [ ] Event logging, block rationale

### 8. Threat Intelligence
- [ ] Feed-updater scripts
- [ ] Rule syncing to IDS/honeypot

### 9. Reporting/Notifications
- [ ] Report generation scripts (HTML)
- [ ] UI/push/email notifications

### 10. Voice Assistant Module (MCP/Agent)
- [ ] Integrate Mycroft AI or similar for voice control/feedback
- [ ] Develop event-driven speech and interactive device management logic

### 11. NAC & Device Management
- [ ] Scripts/UI for device isolation/kicking and network segmentation

### 12. Anonymity & Traffic Routing
- [ ] TOR/Proxy routing for selective/opt-in privacy
- [ ] OpenVPN integration for secure encrypted access (low priority)

### 13. Versatile Home-Lab Features
- [ ] NAS module (low priority)
- [ ] WSL compatibility enhancers

### 14. Docker Orchestration
- [ ] Compose setup for all modules

### 15. Documentation & Community
- [x] Per-module READMEs
- [x] ADRs, setup, contributing, roadmap

---
> Contributors can pick any module/task above, follow module README and docs, and work independently without onboarding assistance. All philosophy and docs are to be followed and improved!
