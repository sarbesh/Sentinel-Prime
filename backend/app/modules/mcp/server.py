from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import datetime

router = APIRouter(prefix="/mcp", tags=["mcp"])

class AgentInfo(BaseModel):
    name: str
    version: str
    description: str
    capabilities: list[str]

class TaskRequest(BaseModel):
    task_id: str
    description: str
    parameters: Dict[str, Any] = {}

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    timestamp: str

class StatusResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Mock agent info
AGENT_INFO = AgentInfo(
    name="Sentinel Prime MCP Agent",
    version="1.0.0",
    description="MCP agent for Sentinel Prime threat intelligence platform",
    capabilities=[
        "threat_intelligence",
        "network_monitoring",
        "vulnerability_assessment",
        "incident_response"
    ]
)

# In-memory task store (for demonstration)
tasks: Dict[str, TaskResponse] = {}

@router.get("/agent", response_model=AgentInfo)
async def get_agent_info():
    """Return information about the MCP agent."""
    return AGENT_INFO

@router.get("/status", response_model=StatusResponse)
async def get_mcp_status():
    """Return the status of the MCP server."""
    return StatusResponse(
        status="operational",
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        version="1.0.0"
    )

@router.post("/task", response_model=TaskResponse)
async def submit_task(task_request: TaskRequest):
    """Submit a task for the MCP agent to process."""
    # In a real implementation, this would queue the task for processing
    task_response = TaskResponse(
        task_id=task_request.task_id,
        status="accepted",
        result={"message": "Task submitted for processing"},
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    tasks[task_request.task_id] = task_response
    return task_response

@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """Get the status and result of a submitted task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

# Health check for MCP endpoint
@router.get("/health")
async def mcp_health():
    """Health check for the MCP service."""
    return {"status": "healthy", "service": "mcp"}
