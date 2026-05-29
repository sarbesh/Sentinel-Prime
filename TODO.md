# TODO List for SENTINEL PRIME Project

## Completed Tasks
- [x] Initialize git repository and fix any lock issues
- [x] Fix import errors (pydantic_settings) in backend
- [x] Rebuild Docker images and start containers
- [x] Verify backend health endpoint is working
- [x] Integrate backend with React web-ui: configure API URL and test connectivity (basic health check in web-ui)
- [x] Make application MCP ready: add MCP server endpoints to backend (e.g., /mcp/* )
- [x] Test MCP endpoints
- [x] Perform documentation after each step: update README.md, create TODO.md, and update any relevant docs
- [x] Maintain a TODO file tracking completed and pending tasks (ongoing)
- [x] Set up Cypress for end-to-end testing
- [x] Create a basic Cypress test for web UI
- [x] Create a cron job script to check for active subagent work on sentinel project
- [x] Schedule the cron job to run daily using OpenClaw gateway cron
- [x] Updated README.md to document MCP capabilities and network recon/IDS features

## In Progress Tasks
- [ ] Create more comprehensive tests for critical user flows
- [ ] Implement actual subagent spawning mechanism when no work is detected (the cron job currently only checks)
- [ ] Extend Dockerfile with privileged capabilities and network tools (nmap/suricata) for active scanning
- [ ] Implement actual network scanning and IDS/IPS execution via MCP tasks

## Pending Tasks
- [ ] Add user authentication and authorization to API and MCP endpoints
- [ ] Implement vector-based similarity search for threat patterns using pgvector
- [ ] Expand threat intelligence feeds beyond OTX and Abuse.ch
- [ ] Implement actual scanning triggers when new devices are detected (extend DHCP listener)
- [ ] Create production deployment documentation with security considerations

## E2E Testing
- [x] Set up Cypress for end-to-end testing
- [x] Create a basic Cypress test for web UI
- [ ] Create more comprehensive tests for critical user flows

## Cron Job
- [x] Create a script to check for active subagent work on sentinel project
- [x] Schedule the script to run daily using OpenClaw gateway cron (via exec on gateway)
- [ ] Implement actual subagent spawning mechanism when no work is detected
