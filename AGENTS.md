# AGENTS.md

## Quick Commands
- **Docker**: `docker-compose up -d --build`; `docker-compose down`; `docker logs -f [service]`
- **Backend dev**: `cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload`
- **Backend lint**: `pip install flake8 black isort && flake8 . && black . && isort .`
- **Backend test**: `pytest` (all) or `pytest backend/tests/` (folder) or `pytest -k <name>`
- **Frontend dev**: `cd web-ui/web-ui && npm install && npm start`
- **Frontend build**: `./web-ui/scripts/build.sh <platform>` (web|android|ios|desktop|all)
- **Frontend lint**: `npm install --save-dev eslint prettier && npx eslint . && npx prettier --write .`

## Structure
```
sentinel-prime/
├─ backend/      # FastAPI API
├─ web-ui/       # Expo/React Native (web, android, ios, desktop)
├─ honeypot/     # placeholder modules
├─ ips-ids/
├─ network‑scanner/
└─ docker-compose.yml
```

## Conventions
- **Python**: black (88), isort, type hints, SQLModel, HTTPException for errors.
- **JS**: Prettier (2‑space, single quotes), camelCase vars, PascalCase components.
- **API**: JSON bodies, CORS, Pydantic models, FastAPI Depends for DB.
- **MCP**: tools named `verb_noun`; register in `backend/mcp_server/server_sse.py`; API‑key auth.
- **Branching**: `feature/…` or `fix/…`; never commit without explicit request.
- **Critical**: no secrets in repo; lint before commit; DB path `/app/data/sentinel_prime.db`.

*These concise notes cover the high‑signal guidance an agent must not miss.*