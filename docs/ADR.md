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

---

> For every new major technical decision, please add a new ADR entry with date, context, alternatives, and rationale.
