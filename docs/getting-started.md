# Getting Started with SENTINEL PRIME

## Overview
SENTINEL PRIME is a home network security and monitoring suite. All modules are containerized and documented independently so anyone can pick up any task and contribute.

## Quickstart
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd sentinel-prime
   ```
2. Read `README.md` for high-level project info and architectural diagram.
3. Explore `/docs/ADR.md` for technical decision history.
4. See `/docs/tasks.md` for current TODOs and module breakdown.
5. To work on a specific module, check its directory and local `README.md` for instructions and relevant APIs/setup.
6. To contribute, read `CONTRIBUTING.md`.
7. Launch basic stack (when available):
   ```bash
   docker-compose up --build
   ```

## Directory Structure
- All modules have their own README with usage and API.
- Docs folder includes architecture/walkthroughs/decision rationale.

## No Questions? Everything Documented!
This project values clear, up-to-date documentation. If you spot anything unclear, please open a PR or issue to improve it!

---
