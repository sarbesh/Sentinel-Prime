# AGENTS.md

## Coding, Testing, and Contribution Guidelines for Agentic Workflows

---

Welcome to the Sentinel Prime codebase! This document provides standardized workflows, formatting, and coding style rules for autonomous agents and human contributors.

**NOTE:** No Cursor or Copilot rules files exist in this repository; this AGENTS.md governs agent operations.

---

## 1. Build, Lint, and Test Commands

**Copy-paste exact commands. Agents must not guess.**

### Docker (Primary Deployment)
```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f              # All services
docker-compose logs -f backend      # Backend only

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# Access container shell
docker exec -it sentinel-prime-backend sh
```

### Python/FastAPI Backend (Development)
```bash
# Navigate to backend and create venv
cd backend && python3 -m venv .venv && source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Run server (dev)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Lint (required before commit)
pip install flake8 black isort && flake8 . && black . && isort .

# Test
pytest                          # Run all tests
pytest backend/tests/          # All tests in folder
pytest backend/tests/test_x.py  # Single test file
pytest -k test_func_name       # Single test by name pattern
pytest -v --tb=short           # Verbose with short traceback
```

### JS/React Native Frontend (Expo) - Multi-Platform
```bash
# Install Node LTS via NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install --lts && nvm use --lts

# Install project deps
cd web-ui/web-ui && npm install

# Run app (dev)
npm start              # Start Expo
npm run web           # Web only
npm run android       # Android only
npm run ios           # iOS only

# Build all platforms using script
chmod +x web-ui/scripts/build.sh
./web-ui/scripts/build.sh web        # Web (React Native Web)
./web-ui/scripts/build.sh android    # Android APK
./web-ui/scripts/build.sh ios        # iOS (macOS only)
./web-ui/scripts/build.sh desktop    # Windows/Linux/Mac desktop (Electron)
./web-ui/scripts/build.sh all        # All platforms

# Lint (required before commit)
npm install --save-dev eslint prettier && npx eslint . && npx prettier --write .
```

---

## 2. Project Structure

```
sentinel-prime/
├── backend/              # FastAPI backend (api/, main.py, models.py, database.py)
├── web-ui/              # Multi-platform app
│   ├── web-ui/         # Expo/React Native source
│   ├── desktop/        # Electron desktop wrapper
│   ├── docker/         # nginx web container
│   └── scripts/        # Build scripts
├── honeypot/            # Honeypot module (placeholder)
├── ips-ids/             # IPS/IDS module (placeholder)
├── network-scanner/     # Network scanner module (placeholder)
├── docker-compose.yml   # Orchestrates backend + ui containers
└── AGENTS.md           # This file
```

---

## 3. Python Code Style & Conventions

- **Imports:** Absolute within project. Standard lib → third party → local; use isort.
- **Formatting:** Use black (88 char limit). Run: `black backend/`
- **Type Hints:** Use for all functions/models (PEP484). Use SQLModel types.
- **Naming:** Classes: CamelCase, functions/vars: snake_case, files: lowercase.
- **Error Handling:** Use HTTPException for API errors.

---

## 4. API Design Conventions

- **Auth:** Accept JSON body (not form data) for mobile/app compatibility.
- **CORS:** Always include CORS middleware for cross-origin requests.
- **Response Models:** Use Pydantic models for all API responses.
- **Dependencies:** Use FastAPI `Depends()` for DB session injection.

---

## 5. JavaScript/React Native Code Style

- **Imports:** External libraries first, then project files. Use relative paths where appropriate.
- **Formatting:** Use Prettier (2 spaces, trailing commas, single quotes).
- **API URL:** Use dynamic URL based on hostname.
- **Naming:** Components: PascalCase, vars/functions: camelCase, files: camelCase/kebab-case.
- **Error Handling:** Use try/catch in async functions.

---

## 6. Error Handling & Logging

- **Logging is critical** for maintainability
- Never expose internal errors to end users (sanitize messages)
- Log with enough context (request IDs, user context, parameters)
- Actionable user feedback (e.g., "Invalid IP; must be IPv4")
- Prefer early returns to avoid deep nesting

---

## 7. Critical Constraints

- **Never commit secrets, keys, or credentials** (SECRET_KEY, passwords, API keys)
- **Never skip linting** before committing
- Keep AGENTS.md under 150 lines; detailed docs in README.md
- Use pre-commit hooks for lint, typecheck, secret scanning
- Database path: `/app/data/sentinel_prime.db` (not `./sentinel_prime.db`)

---

## 8. Branching & Commit Workflow

- **Every major feature/todo** must be developed in its own branch
- Branch naming: `feature/<feature-name>` or `fix/<bug-description>`
- **Never commit unprompted** - only commit when the user explicitly asks or appreciates the work
- When the user asks to save/commit the changes, create a branch and commit all changes
- Commit message format: `<type>: <description>` (e.g., `feat: add auto-update feature`)
- After user approval, create PR or merge to main
- Always run lint/typecheck before commit

---

*Follow these rules to keep Sentinel Prime modular, agent-ready, and human-friendly!*
