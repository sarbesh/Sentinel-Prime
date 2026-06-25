# SENTINEL PRIME Project Plan

## Executive Summary
SENTINEL PRIME is an open-source, sci-fi-inspired, modular honeypot and network threat monitoring suite for home networks. The project has a solid foundation with:
- Dockerized architecture with separate services for backend, scanner, UI, vector DB, MCP, honeypot, and IPS/IDS
- Backend built with FastAPI/Python
- Frontend built with React Native (web UI via Docker)
- Core modules implemented: alerts, auth, devices, downloads, honeypot, ips, network, scans, settings, sse, todos, updates, version
- Database: SQLite with vector DB (PostgreSQL + pgvector) integration
- Docker Compose orchestration already in place

Based on the roadmap and current state, the project is well underway but needs completion of several key modules and refinement of existing ones.

## Planning Approach
This plan breaks down work into three types of subagent tasks:
1. **Decision Subagents**: For architectural decisions, technology choices, and prioritization
2. **Architectural Subagents**: For designing system components, APIs, and data models
3. **Execution Subagents**: For implementing features, fixing bugs, and writing code

## Current State Analysis

### Completed/In Progress:
- [x] Project initialization, licensing, README
- [x] Base documentation and ADRs
- [x] Backend API structure with FastAPI
- [x] Database models and initialization
- [x] Docker Compose setup for all services
- [x] Basic UI container setup
- [x] Scanner module (Nmap-based)
- [x] Honeypot module (OpenCanary-based)
- [x] IPS/IDS module (Suricata-based)
- [x] Vector DB integration for AI/ML capabilities
- [x] MCP (Model Context Protocol) server for AI integration
- [x] Alert system with SSE (Server-Sent Events)
- [x] Device monitoring and tracking
- [x] Network scanning capabilities
- [x] Downloads management
- [x] Settings management
- [x] Version tracking
- [x] Todo management API

### Needing Work (from Roadmap):
- [ ] Web & Mobile Unified UI (React Native codebase scaffold, Auth, dashboard, device config)
- [ ] Backend/API modular endpoints enhancement
- [ ] Network scanner UI/DB integration
- [ ] New device monitor (DHCP listener) integration and scan trigger
- [ ] IPS/IDS alert/report pipeline to UI enhancement
- [ ] Honeypot event logging and block rationale enhancement
- [ ] Threat intelligence feed-updater scripts and rule syncing
- [ ] Report generation scripts (HTML) and UI/push/email notifications
- [ ] Voice assistant module (Mycroft AI or similar)
- [ ] NAC & device management scripts/UI for isolation/kicking
- [ ] Anonymity & traffic routing (TOR/Proxy, OpenVPN)
- [ ] Versatile home-lab features (NAS module, WSL compatibility)
- [ ] Final Docker orchestration refinement
- [ ] Documentation and community improvements (per-module READMEs already done)

## Detailed Task Breakdown

### 1. Decision Subagent Tasks

#### 1.1 Technology Stack Review
- Evaluate current tech choices (FastAPI, React Native, Docker, PostgreSQL+pgvector, SQLite)
- Assess if any components need modernization or replacement
- Decision: Keep current stack or migrate to alternatives

#### 1.2 UI Framework Decision
- Current: React Native for unified web/mobile
- Evaluate: Flutter, Ionic, or separate web (React) + mobile (React Native) approaches
- Decision: Confirm React Native or choose alternative

#### 1.3 Database Strategy Decision
- Current: SQLite for main DB, PostgreSQL+pgvector for vector DB
- Evaluate: Single PostgreSQL instance for both, or keep separate
- Decision: Optimize database architecture

#### 1.4 Authentication & Authorization Decision
- Review current auth implementation in backend/api/auth.py
- Evaluate need for OAuth2, JWT refinement, role-based access control (RBAC)
- Decision: Enhance auth system if needed

#### 1.5 Deployment & DevOps Decision
- Review current Docker Compose setup
- Evaluate need for Kubernetes, Helm charts, or improved CI/CD
- Decision: Optimize deployment strategy

### 2. Architectural Subagent Tasks

#### 2.1 UI Architecture
- Design React Native app structure for web/mobile unification
- Plan navigation, state management (Redux/Zustand/context), and API service layer
- Design responsive layouts for different screen sizes
- Plan offline capabilities and data synchronization

#### 2.2 Backend API Architecture
- Design modular API structure following RESTful principles
- Plan API versioning strategy
- Design WebSocket/SSE implementation for real-time updates
- Plan rate limiting, caching, and performance optimizations
- Design plugin architecture for easy module addition

#### 2.3 Data Model Architecture
- Review current models in backend/models.py
- Design relationships between devices, scans, alerts, honeypot events, IDS events
- Plan vector embedding storage and retrieval strategies
- Design audit logging and data retention policies

#### 2.4 Module Integration Architecture
- Design standardized interfaces for all modules (scanner, honeypot, IDS, etc.)
- Plan event-driven architecture for module communication
- Design configuration management system for modules
- Plan health checking and monitoring for all services

#### 2.5 Security Architecture
- Design threat intelligence integration pipeline
- Plan automated response mechanisms (block IPs, isolate devices)
- Design secure communication between services
- Plan vulnerability scanning and dependency management

### 3. Execution Subagent Tasks

#### 3.1 UI Implementation Tasks
- Scaffold React Native project with Expo or bare workflow
- Implement authentication screens (login, register, forgot password)
- Create dashboard with network overview, threat level, recent alerts
- Implement device listing and detail views
- Create scan configuration and execution interface
- Implement honeypot and IDS event viewers
- Create settings management interface
- Implement push notifications and real-time updates
- Create reporting and export functionality

#### 3.2 Backend Enhancement Tasks
- Enhance auth API with refresh tokens, password reset, email verification
- Improve device API with MAC vendor lookup, OS fingerprinting, device profiling
- Enhance scan API with scheduling, custom scan profiles, incremental scanning
- Improve alert API with severity levels, deduplication, enrichment
- Enhance honeypot API with geolocation, threat intelligence correlation
- Improve IDS API with rule management, false positive reduction
- Add API documentation (OpenAPI/Swagger) enhancements
- Implement background workers for periodic tasks

#### 3.3 Module Integration Tasks
- Integrate new device monitor (DHCP listener) to trigger automatic scans
- Enhance scanner to automatically upload results to backend
- Improve honeypot to send enriched events with threat intelligence
- Enhance IDS to automatically block malicious IPs via firewall integration
- Implement threat intelligence feed updater (OTX, Abuse.ch, etc.)
- Create automated rule synchronization for IDS/honeypot
- Implement network topology mapping and visualization

#### 3.4 Reporting & Notification Tasks
- Implement HTML/PDF report generation for scans, events, and summaries
- Create email notification system for critical alerts
- Implement push notifications via Firebase/Apple Push Notification service
- Create webhook integrations for third-party services (Slack, Discord, etc.)
- Implement scheduled report generation and delivery

#### 3.5 Advanced Feature Tasks
- Implement voice assistant module using Mycroft or similar
- Create network access control (NAC) interface for device isolation/kicking
- Implement TOR/Proxy routing for opt-in privacy features
- Add OpenVPN integration for secure remote access
- Create NAS module for storage integration (low priority)
- Enhance WSL compatibility for development purposes

#### 3.6 DevOps & Quality Tasks
- Optimize Docker images for size and security
- Implement health checks for all services
- Create CI/CD pipeline for automated testing and deployment
- Add comprehensive logging and monitoring (ELK stack or similar)
- Implement automated backup and disaster recovery procedures
- Add security scanning and vulnerability assessment
- Create performance benchmarking and optimization scripts

## Priority Order (Based on Roadmap)

### Phase 1: Core Completion (Immediate)
1. UI Implementation - Basic React Native app with auth and dashboard
2. Backend Enhancements - Auth improvements, device management
3. Module Integration - New device monitor trigger, scanner/honeypot/IDS integration
4. Basic Reporting - HTML report generation

### Phase 2: Enhanced Features (Near-term)
1. Advanced Reporting - PDF reports, email notifications
2. Threat Intelligence - Feed integration and rule synchronization
3. Voice Assistant - Basic voice command implementation
4. NAC Features - Device isolation and kicking capabilities

### Phase 3: Advanced & Polish (Long-term)
1. Anonymity Features - TOR/Proxy and OpenVPN integration
2. Home Lab Features - NAS module and WSL enhancements
3. Performance Optimization - Caching, load testing, scaling
4. Polish & Documentation - Final UI/UX improvements, comprehensive docs

## Success Metrics
- All roadmap items completed or have clear implementation paths
- System runs stably in Docker Compose with health checks passing
- UI provides intuitive interaction with all core features
- Modules communicate effectively through well-defined interfaces
- Security best practices implemented throughout
- Documentation is comprehensive and easy to follow
- Community contribution process is clear and welcoming

## Dependencies and Risks
- **Dependencies**: Docker, Docker Compose, Node.js, Python 3.14+, PostgreSQL
- **Technical Risks**: 
  - UI framework choice affecting development speed
  - Database performance with large datasets
  - Real-time update scalability
  - Integration complexity between diverse modules
- **Mitigation Strategies**:
  - Spike implementations for risky components
  - Modular design to allow technology swaps
  - Comprehensive testing strategy
  - Incremental delivery with frequent integration

## Next Steps
1. Review this plan with stakeholders
2. Assign decision subagents for technology choices
3. Begin UI scaffolding and basic backend enhancements
4. Set up development environment for contributors