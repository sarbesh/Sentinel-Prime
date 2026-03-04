# Development Guide: SENTINEL PRIME

## Philosophy
- Modular: Each new feature is an independent module, documented and decoupled.
- Clear: All code is commented, all APIs documented, all major decisions logged in ADR.md.
- Onboarding: Each module has a README with setup, integration, and contribution guide.

## Workflow
1. Pick any issue/task from `/docs/tasks.md` or GitHub issues
2. Read the ADR and docs for context
3. Review the module's README for details
4. Branch from latest main: `git checkout -b feature/<module/feature>`
5. Build, test, and document your changes
6. Submit PR, updating docs/README/ADR as needed
7. Review and merge via GitHub

## Coding Standards
- Keep code readable, modular, and loosely coupled.
- Add/extend documentation with every major change.
- Test your code—unit/integration, as fits your module.

## Docs-First Approach
- Update docs and READMEs before coding if the change is architectural.
- Each module's API, config, and behavior should allow any agent/human to understand and extend the module independently.
- ADR.md records every key decision, rationale, and alternatives.

## Getting Help
- Everything should be documented. If not, open a PR or issue to fix it!
- Discussions, support, Q&A managed via GitHub Discussions (when enabled).
