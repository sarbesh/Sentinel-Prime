# Architecture Decision Records (ADR)

This file logs major technical decisions made for SENTINEL PRIME. Each entry includes context, alternatives considered, rationale for the choice, and guidance for future contributors.

## ADR-001: Modular, Containerized Architecture
- **Date:** 2026-03-04
- **Decision:** Use Docker Compose to orchestrate independent containers for scanner, honeypot, IPS/IDS, backend, unified UI, etc.
- **Alternatives:** Monolithic app, VMs, single binary
- **Rationale:** Maximizes flexibility and ability to swap, add, upgrade modules. Lowest friction for new features and contributors.
- **Impact:** Contributors build modules in their own folders; each module can be understood, tested, and replaced independently. 

## ADR-002: Unified UI With React Native
- **Date:** 2026-03-04
- **Decision:** Use React Native for both web and mobile (export via react-native-web)
- **Alternatives:** Separate web (React/Angular/Vue) and native mobile (Swift/Kotlin)
- **Rationale:** Reduces code duplication, maintenance; enables contributors to focus on features and user experience in one codebase.
- **Impact:** UI contributions benefit both web and mobile. Testing and onboarding unified for all platforms.

## ADR-003: "Open For Change" Philosophy
- **Date:** 2026-03-04
- **Decision:** All major documentation and source files must be clear, modular, and up-to-date so any contributor (human/AI) can pick up and progress independently.
- **Alternatives:** Ad-hoc docs, email/onboarding dependency
- **Rationale:** Enables scalable, asynchronous teamwork and project evolution. AI/automation can assist anywhere.
- **Impact:** ADR is kept updated. Each module has its own README (purpose, setup, API). Global docs point to all context. Minimal onboarding friction.

## ADR-004: Documentation-Driven Development & Per-Module READMEs
- **Date:** 2026-03-04
- **Decision:** Every module must have a dedicated README, and docs for onboarding, tasks/todo, development guide, and roadmap must be maintained. Major changes require accompanying ADR and documentation updates.
- **Alternatives:** Central README only, oral onboarding
- **Rationale:** Ensures total clarity and enables any contributor/agent to start without need for further inquiry. Empowers asynchronous and distributed development, including AI agents.
- **Impact:** All folders contain descriptive README.md, which, together with ADR and getting-started, provide complete context.

## ADR-005: Prioritization of Core Security, Voice, and NAC Over VPN/NAS
- **Date:** 2026-03-04
- **Decision:** Focus development on core modules: IDS/IPS, device monitor, honeypot, threat intelligence, voice agent, and device management (NAC). OpenVPN and NAS functionality are low-priority, opt-in enhancements.
- **Alternatives:** Build all features at equal priority/phase 1.
- **Rationale:** Most users value real-time security, device management, and event-driven control first. These features power the interactive/voice agent model and are foundational. VPN and NAS are enthusiast features, optional add-ons for advanced home labs.
- **Impact:** Roadmap and TODO list reflect priorities—contributors should focus on core before VPN/NAS modules. Docs and onboarding stress the modular opt-in approach.

---

> For every new major technical decision, please add a new ADR entry with date, context, alternatives, and rationale.

## ADR-006: MCP Gateway Architecture for AI Integration
- **Date:** 2026-03-12
- **Decision:** Implement Sentinel Prime as an MCP Gateway that aggregates tools from multiple MCP servers (local Sentinel tools + remote Kali Linux MCP server) into a unified API.
- **Alternatives:**
  1. Standalone MCP servers - Multiple separate MCP connections for each component
  2. MCP Gateway (chosen) - Single entry point aggregating all tools
- **Rationale:** 
  - Single authentication point for AI clients
  - Unified tool namespace simplifies AI prompting
  - Centralized logging and access control
  - Allows future extension to other security tools (Metasploit, OpenVAS, etc.)
- **Impact:** 
  - AI clients connect to single MCP endpoint
  - Gateway proxies requests to appropriate backend (local DB or remote Kali)
  - Enables advanced penetration testing workflows via natural language

## ADR-007: MCP Server Authentication Strategy
- **Date:** 2026-03-12
- **Decision:** Use API key authentication via `x-api-key` header for MCP server access, configurable via environment variable or database-stored keys.
- **Alternatives:**
  1. OAuth2/JWT authentication
  2. API Key (chosen)
  3. No authentication (development only)
- **Rationale:** 
  - Simple to implement and use with MCP clients
  - Compatible with all MCP client types
  - Supports both Docker and native deployments
  - Keys can be rotated via UI or API
- **Impact:** All MCP endpoints require valid API key; keys stored in settings table or env vars
