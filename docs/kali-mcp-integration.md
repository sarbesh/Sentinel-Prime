# Kali MCP Integration

## Overview

This document describes how to integrate Sentinel Prime with Kali Linux MCP Server to provide AI-powered penetration testing capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sentinel Prime MCP Client                     │
│  (Orchestrates all MCP connections)                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
┌─────────────────┐     ┌─────────────────────────────┐
│  Local MCP      │     │   Kali MCP Server          │
│  Server         │     │   (Docker/Remote)          │
│  (Sentinel)     │     │   - Nmap                   │
│  - list_devices │     │   - Nikto                  │
│  - get_alerts   │     │   - Hydra                 │
│  - trigger_scan │     │   - SQLMap                 │
│  - etc.         │     │   - Metasploit            │
└─────────────────┘     └─────────────────────────────┘
```

## Prerequisites

- Sentinel Prime MCP Server (already implemented)
- Kali Linux with MCP Server (see Options below)
- AI Client (Claude Desktop, Claude Code, etc.)

## Kali MCP Server Options

### Option 1: Docker (Recommended for Testing)

```bash
# Quick start with Docker
docker run -dit \
  --name kali-mcp \
  -p 8081:8081 \
  kalilinux/kali-last-shot

# Or use docker-compose (see below)
```

### Option 2: Native Kali Linux

On a Kali Linux system:

```bash
# Install Kali MCP Server
sudo apt update
sudo apt install mcp-kali-server

# Start the server
mcp-kali-server --port 8081
```

### Option 3: Custom Kali MCP Server

Build your own with specific tools:

```bash
# Clone a custom Kali MCP server
git clone https://github.com/rangta10/kali-mcp-server
cd kali-mcp-server
npm install
npm start
```

## Implementation Plan

### Phase 1: MCP Gateway Architecture

Create `backend/mcp/kali_client.py`:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx

class KaliMcpClient:
    """Client for connecting to remote Kali MCP servers."""
    
    def __init__(self, server_url: str, api_key: str = None):
        self.server_url = server_url
        self.api_key = api_key
        self.session = None
    
    async def connect(self):
        """Establish connection to Kali MCP server."""
        # HTTP-based connection for remote servers
        self.client = httpx.AsyncClient()
    
    async def execute_tool(self, tool_name: str, arguments: dict):
        """Execute a tool on the Kali MCP server."""
        response = await self.client.post(
            f"{self.server_url}/tools/{tool_name}",
            json=arguments,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
    
    async def list_tools(self):
        """List available tools on Kali MCP server."""
        response = await self.client.get(
            f"{self.server_url}/tools",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()
```

### Phase 2: API Endpoints

Add to `backend/api/mcp.py`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp/kali/connect` | POST | Configure Kali MCP server connection |
| `/mcp/kali/disconnect` | POST | Disconnect from Kali server |
| `/mcp/kali/status` | GET | Get connection status |
| `/mcp/kali/tools` | GET | List available Kali tools |
| `/mcp/kali/execute` | POST | Execute a Kali tool |

### Phase 3: Tool Proxy

Forward tool calls from AI clients to Kali MCP server:

```python
@app.post("/mcp/kali/execute")
async def execute_kali_tool(
    tool: str,
    arguments: dict,
    kali_config: KaliConfig = Depends(get_kali_config)
):
    client = KaliMcpClient(kali_config.url, kali_config.api_key)
    result = await client.execute_tool(tool, arguments)
    return result
```

## Docker Compose Integration

Add to `docker-compose.yml`:

```yaml
  kali-mcp:
    image: kalilinux/kali-last-shot
    container_name: sentinel-prime-kali
    ports:
      - "8081:8081"
    volumes:
      - kali-data:/root
    privileged: true
    environment:
      - KALI_MCP_PORT=8081
      - KALI_MCP_AUTH=${KALI_MCP_API_KEY}
    networks:
      - sentinel-prime-network

  mcp:
    build: ./backend
    container_name: sentinel-prime-mcp
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=sqlite:////data/sentinel_prime.db
      - MCP_PORT=8001
      - MCP_API_KEY=${MCP_API_KEY}
      - KALI_MCP_URL=http://kali-mcp:8081
    depends_on:
      - kali-mcp
    networks:
      - sentinel-prime-network
```

## Available Kali Tools

Once integrated, these tools will be available:

| Tool | Description |
|------|-------------|
| `nmap` | Network scanning and enumeration |
| `nikto` | Web vulnerability scanning |
| `hydra` | Password brute-forcing |
| `sqlmap` | SQL injection testing |
| `msfconsole` | Metasploit Framework |
| `gobuster` | Directory/file enumeration |
| `dirb` | Web content scanner |
| `whois` | WHOIS lookup |
| `dig` | DNS enumeration |
| `ping` | Host reachability |
| `curl` | HTTP requests |
| `wpscan` | WordPress security scanner |

## Security Considerations

1. **Authentication**: All Kali MCP connections require API key
2. **Network Isolation**: Run Kali container in isolated network
3. **Rate Limiting**: Implement rate limits on tool execution
4. **Tool Allowlist**: Restrict which tools can be executed
5. **Audit Logging**: Log all tool executions for review
6. **Resource Limits**: Limit CPU/memory for container

## Usage Examples

### Connect to Kali MCP Server

```bash
curl -X POST http://localhost:8000/mcp/kali/connect \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "url": "http://kali-mcp:8081",
    "api_key": "your-kali-api-key"
  }'
```

### Execute Nmap Scan via MCP

```json
{
  "tool": "nmap",
  "arguments": {
    "target": "192.168.1.1/24",
    "scan_type": "quick",
    "ports": "22,80,443"
  }
}
```

### AI Client Configuration

```json
{
  "mcpServers": {
    "sentinel-prime": {
      "url": "http://localhost:8001",
      "headers": {
        "x-api-key": "your-sentinel-api-key"
      }
    },
    "kali-tools": {
      "url": "http://localhost:8081",
      "headers": {
        "x-api-key": "your-kali-api-key"
      }
    }
  }
}
```

## Troubleshooting

### Connection Refused
- Verify Kali MCP server is running: `curl http://localhost:8081/health`
- Check network connectivity between containers

### Authentication Failed
- Verify API keys match on both sides
- Check server logs for authentication errors

### Tool Not Found
- List available tools: `GET /mcp/kali/tools`
- Verify tool is installed in Kali container

## References

- [Kali MCP Server - GitHub](https://github.com/rangta10/kali-mcp-server)
- [Kali MCP Server - GitLab](https://gitlab.com/kalilinux/packages/mcp-kali-server)
- [Model Context Protocol Documentation](https://modelcontextprotocol.io)
- [Claude Desktop MCP Configuration](https://docs.anthropic.com/en/docs/claude-desktop)

---

*Last updated: March 2026*
