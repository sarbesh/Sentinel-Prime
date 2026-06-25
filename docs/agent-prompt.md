---
applyTo: '**'
---

# SENTINEL PRIME: AI Agent Interaction Prompt

## Project Overview

You are working on SENTINEL PRIME, an open-source home network security suite inspired by sci-fi themes. The project is modular, extensible, and designed for security enthusiasts.

## Guidelines
- Modular architecture: Each feature (honeypot, IPS/IDS, network scanner, threat intel, device monitor) exists as a standalone container/module, orchestrated via Docker Compose.
- Unified UI: React Native project, single codebase for mobile/web, modules expose unified APIs for interoperability.
- Documentation-first: Every module/feature has a local README, module-level ADRs, API reference, and onboarding instructions. Architectural decisions and development guidelines are maintained in docs/ and referenced from README.md and CONTRIBUTING.md.
- Scifi-inspired UX: Balance advanced functionality with thematic, accessible interface.
- Expandability: Open to new modules, integrations, and architecture changes at any time. Code and docs structured for autonomous continuation.
- Security first: Prioritize IDS/IPS, honeypot, scanner, threat intelligence, device management; VPN (OpenVPN) and NAS/forensics are optional enhancements.
- Onboarding-welcome: Contributors/agents must be able to pick up any module/task with only documentation/context (no direct onboarding required).

## AI Agent Workflow
1. Read all relevant docs (README.md, docs/, module READMEs) before acting.
2. Break down tasks into actionable steps (todo list) and track progress.
3. Update/reference ADRs and docs for every decision — all changes are logged.
4. Contribute modular code using established patterns. New modules should have clear READMEs and integration notes.
5. Ensure interoperability by defining APIs and updating unified UI registry as needed.
6. Test code and update test plans for every new/modified module.
7. Keep contributor docs up-to-date — add links to new docs/prompt files in CONTRIBUTING.md.

## How to Use This Prompt
- Reference this file when launching an AI agent, contributor onboarding, or architectural review.
- Update this file for major changes or expansions.
- Link to this file in CONTRIBUTING.md, README.md, and onboarding docs.

---

*Maintained for autonomous AI/human agents to maximize continuity, clarity, and modularity in SENTINEL PRIME.*
