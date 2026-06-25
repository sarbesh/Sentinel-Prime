#!/bin/bash
# Sentinel Prime Deployment Verification Script
# Run this after `docker-compose up -d` to verify all services are healthy

set -e

echo "=== Sentinel Prime Deployment Verification ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# Check 1: All containers running
echo "1. Checking container status..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Containers are running"
else
    echo -e "${RED}✗${NC} Some containers are not running"
    docker-compose ps
    FAILURES=$((FAILURES + 1))
fi

# Check 2: Backend health endpoint
echo ""
echo "2. Checking backend health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Backend health endpoint responding (HTTP $HEALTH_RESPONSE)"
else
    echo -e "${RED}✗${NC} Backend health endpoint failed (HTTP $HEALTH_RESPONSE)"
    FAILURES=$((FAILURES + 1))
fi

# Check 3: API endpoints returning data
echo ""
echo "3. Checking API endpoints..."
for endpoint in "/devices" "/scans" "/alerts" "/vulnerabilities"; do
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000${endpoint}" 2>/dev/null || echo "000")
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}✓${NC} GET ${endpoint} - HTTP $RESPONSE"
    else
        echo -e "${RED}✗${NC} GET ${endpoint} - HTTP $RESPONSE"
        FAILURES=$((FAILURES + 1))
    fi
done

# Check 4: Web UI accessibility
echo ""
echo "4. Checking web UI accessibility..."
UI_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$UI_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Web UI responding (HTTP $UI_RESPONSE)"
else
    echo -e "${RED}✗${NC} Web UI failed (HTTP $UI_RESPONSE)"
    FAILURES=$((FAILURES + 1))
fi

# Check 5: React app is loading (check for root div)
echo ""
echo "5. Checking React app is loaded..."
if curl -s http://localhost:3000 | grep -q 'id="root"'; then
    echo -e "${GREEN}✓${NC} React app root element found"
else
    echo -e "${RED}✗${NC} React app root element not found"
    FAILURES=$((FAILURES + 1))
fi

# Check 6: Client-side routing works (test SPA routing)
echo ""
echo "6. Checking SPA routing (try /devices route)..."
DEVICES_ROUTE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/devices 2>/dev/null || echo "000")
if [ "$DEVICES_ROUTE" = "200" ]; then
    echo -e "${GREEN}✓${NC} SPA routing working - /devices returns HTTP $DEVICES_ROUTE"
else
    echo -e "${RED}✗${NC} SPA routing failed - /devices returns HTTP $DEVICES_ROUTE"
    echo "   This might indicate nginx try_files config is missing"
    FAILURES=$((FAILURES + 1))
fi

# Check 7: MCP server health
echo ""
echo "7. Checking MCP server..."
MCP_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/tools \
    -H "x-api-key: sentinel-prime-mcp-default" 2>/dev/null || echo "000")
if [ "$MCP_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓${NC} MCP server responding (HTTP $MCP_RESPONSE)"
else
    echo -e "${RED}✗${NC} MCP server failed (HTTP $MCP_RESPONSE)"
    FAILURES=$((FAILURES + 1))
fi

# Check 8: Database containers
echo ""
echo "8. Checking database services..."
if docker-compose ps vector-db | grep -q "Up"; then
    echo -e "${GREEN}✓${NC} Vector database (PostgreSQL) is running"
else
    echo -e "${RED}✗${NC} Vector database is not running"
    FAILURES=$((FAILURES + 1))
fi

# Final summary
echo ""
echo "=== Verification Summary ==="
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC} Deployment is healthy."
    exit 0
else
    echo -e "${RED}$FAILURES check(s) failed${NC}. Review the output above for details."
    echo ""
    echo "Troubleshooting tips:"
    echo "  - Run 'docker-compose logs' to see service logs"
    echo "  - Check 'docker-compose ps' for container status"
    echo "  - Verify ports 8000, 8001, 3000, 5432 are not in use by other services"
    exit 1
fi