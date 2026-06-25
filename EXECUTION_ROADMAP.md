# SENTINEL PRIME Execution Roadmap

## Overview
This roadmap maps the missing features and enhancements from the planning.md and backend_verification.md to specific subagent tasks, assigning the appropriate worker model based on task complexity.

## Worker Model Constraints
- **nvidia/nvidia/nemotron-3-super-120b-a12b (40 RPM)**: High-complexity logic, architectural refinements, overall coordination (used by coordinator)
- **google/gemma-4-31b-it (15 RPM)**: Core feature implementation, complex API work, UI development
- **google/gemma-4-26b-a4b-it (15 RPM)**: Lighter implementation tasks, documentation, report generation, basic scripts

## Task Mapping

### Phase 1: Core Completion (Immediate)

#### 1.1 UI Implementation - Basic React Native app with auth and dashboard
- **Subagent Task**: Scaffold React Native project with Expo, implement authentication screens (login, register), create dashboard with network overview and threat level.
- **Model**: google/gemma-4-31b-it (15 RPM) - UI development
- **Dependencies**: None
- **Expected Output**: Initialized `web-ui` and `mobile-app` directories with basic React Native/React structure, authentication screens, dashboard component.

#### 1.2 Backend Enhancements - Auth improvements, device management
- **Subagent Task**: Enhance auth API with refresh tokens, password reset, email verification. Improve device API with MAC vendor lookup, OS fingerprinting, device profiling.
- **Model**: google/gemma-4-31b-it (15 RPM) - Core feature implementation, complex API work
- **Dependencies**: Existing auth and device APIs in `/backend/api/auth.py` and `/backend/api/devices.py`
- **Expected Output**: Updated `/backend/api/auth.py` with refresh token flow, password reset, email verification. Updated `/backend/api/devices.py` with MAC vendor lookup and OS fingerprinting enhancements.

#### 1.3 Module Integration - New device monitor trigger, scanner/honeypot/IDS integration
- **Subagent Task**: Integrate new device monitor (DHCP listener) to trigger automatic scans. Enhance scanner to automatically upload results to backend. Improve honeypot to send enriched events with threat intelligence. Enhance IDS to automatically block malicious IPs via firewall integration.
- **Model**: google/gemma-4-31b-it (15 RPM) - Core feature implementation
- **Dependencies**: 
  - Existing DHCP listener in `/dhcp-listener/dhcp_listener.py`
  - Scanner APIs in `/backend/api/scans.py` and `/backend/api/network.py`
  - Honeypot API in `/backend/api/honeypot.py`
  - IDS API in `/backend/api/ips.py`
- **Expected Output**: 
  - Updated DHCP listener that triggers scan API on new device detection
  - Scanner module that posts results to `/api/scans/` endpoint
  - Honeypot module that enriches events with threat intelligence before sending to `/api/honeypot/` 
  - IDS module that automatically updates firewall rules to block malicious IPs

#### 1.4 Basic Reporting - HTML report generation
- **Subagent Task**: Implement HTML report generation engine for scans, events, and summaries.
- **Model**: google/gemma-4-26b-a4b-it (15 RPM) - Lighter implementation tasks, report generation
- **Dependencies**: Existing scan and alert data models in `/backend/models.py`
- **Expected Output**: New `/backend/reports/` directory with HTML report generation scripts, API endpoint in `/backend/api/reports.py` to generate and download reports.

### Phase 2: Enhanced Features (Near-term)

#### 2.1 Advanced Reporting - PDF reports, email notifications
- **Subagent Task**: Extend report generation to PDF format. Create email notification system for critical alerts.
- **Model**: google/gemma-4-26b-a4b-it (15 RPM) - Report generation, lighter implementation
- **Dependencies**: HTML report generation from Phase 1
- **Expected Output**: 
  - PDF report generation capability in `/backend/reports/`
  - Email notification system in `/backend/notifications/` with SMTP integration
  - API endpoints for triggering email notifications

#### 2.2 Threat Intelligence - Feed integration and rule synchronization
- **Subagent Task**: Implement threat intelligence feed updater scripts for OTX, Abuse.ch, VirusTotal. Create automated rule synchronization for IDS/honeypot.
- **Model**: google/gemma-4-31b-it (15 RPM) - Complex API work, integration
- **Dependencies**: 
  - Existing threat intel model in `/backend/models.py`
  - IDS (`/backend/api/ips.py`) and honeypot (`/backend/api/honeypot.py`) APIs
- **Expected Output**:
  - New `/backend/threat_intel_updater/` directory with scripts for OTX, Abuse.ch, VirusTotal
  - Automated rule synchronization scripts that update Suricata rules and OpenCanary configurations
  - Scheduler (cron or background worker) to run updaters periodically

#### 2.3 Voice Assistant - Basic voice command implementation
- **Subagent Task**: Implement voice assistant module using Mycroft or similar MCP integration for voice control/feedback.
- **Model**: google/gemma-4-31b-it (15 RPM) - Complex API work
- **Dependencies**: Existing MCP server in `/backend/mcp_server/`
- **Expected Output**:
  - Voice assistant integration in `/backend/mcp_server/` that listens for voice commands and triggers appropriate actions (scan, device lookup, alert acknowledgment)
  - Basic voice command set: "Start network scan", "Show recent alerts", "Isolate device [MAC]", "Show dashboard"

#### 2.4 NAC Features - Device isolation and kicking capabilities
- **Subagent Task**: Create network access control (NAC) interface for device isolation/kicking via firewall integration.
- **Model**: google/gemma-4-31b-it (15 RPM) - Core feature implementation
- **Dependencies**: 
  - Existing device management APIs
  - IDS alerting system
- **Expected Output**:
  - New `/backend/api/nac.py` with endpoints for isolating and kicking devices
  - Firewall integration (iptables/nftables) to apply isolation rules
  - UI components in web-ui/mobile-app for NAC actions

### Phase 3: Advanced & Polish (Long-term)

#### 3.1 Anonymity Features - TOR/Proxy and OpenVPN integration
- **Subagent Task**: Implement TOR/Proxy routing for opt-in privacy features. Add OpenVPN integration for secure remote access.
- **Model**: google/gemma-4-31b-it (15 RPM) - Complex API work, integration
- **Dependencies**: Network configuration APIs
- **Expected Output**:
  - New `/backend/api/anonymity.py` with TOR/Proxy and OpenVPN configuration and control
  - UI components for enabling/disabling anonymity features
  - Documentation on usage and security considerations

#### 3.2 Home Lab Features - NAS module and WSL enhancements
- **Subagent Task**: Create NAS module for storage integration (low priority). Enhance WSL compatibility for development purposes.
- **Model**: google/gemma-4-26b-a4b-it (15 RPM) - Lighter implementation tasks
- **Dependencies**: Storage and download management APIs
- **Expected Output**:
  - New `/backend/api/nas.py` for NAS integration (SMB/NFS)
  - WSL-specific optimizations in Docker Compose and development scripts
  - Documentation for home lab deployment

#### 3.3 Performance Optimization - Caching, load testing, scaling
- **Subagent Task**: Implement comprehensive caching strategy, create load testing scripts, optimize database queries.
- **Model**: google/gemma-4-31b-it (15 RPM) - Core feature implementation, optimization
- **Dependencies**: Existing API endpoints and database models
- **Expected Output**:
  - Redis caching layer for frequent queries
  - Load testing scripts in `/backend/load_tests/`
  - Optimized database queries with proper indexing
  - API rate limiting implementation

#### 3.4 Polish & Documentation - Final UI/UX improvements, comprehensive docs
- **Subagent Task**: Final UI/UX improvements, comprehensive documentation, onboarding guides.
- **Model**: google/gemma-4-26b-a4b-it (15 RPM) - Documentation, lighter implementation
- **Dependencies**: Completed UI and API components
- **Expected Output**:
  - Polished UI components with consistent design
  - Comprehensive API documentation (OpenAPI/Swagger) enhancements
  - User guides and deployment documentation in `/docs/`
  - Onboarding guide for new contributors

## Coordination Notes

As the SENTINEL PRIME Project Coordinator (using nvidia/nvidia/nemotron-3-super-120b-a12b), I will:
1. Create this execution roadmap
2. Spawn subagents for each task with the appropriate model
3. Monitor progress and provide regular updates to the main agent
4. Verify outputs and ensure integration into the codebase and Docker Compose setup
5. Address any dependencies or blocking issues

## Immediate Next Steps

1. Spawn subagents for Phase 1 tasks (1.1 through 1.4)
2. Wait for completion and verify outputs
3. Integrate outputs and update Docker Compose if needed
4. Report progress to main agent
5. Proceed to Phase 2 tasks

## RPM Considerations

Given the rate limits:
- High-complexity model (coordinator): 40 RPM - sufficient for planning and coordination
- Core feature model: 15 RPM - allows ~4 tasks per hour if each takes one request
- Lighter implementation model: 15 RPM - suitable for documentation and report generation

We will stagger subagent creation to respect rate limits and avoid overwhelming the system.