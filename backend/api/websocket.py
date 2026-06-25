"""
Sentinel Prime - WebSocket Module for Real-time Updates
Enables real-time scan progress, alerts, and threat notifications
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import asyncio
import logging

logger = logging.getLogger('sentinel-websocket')

router = APIRouter()

# Connection manager for active WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.scan_subscribers: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection: {len(self.active_connections)} active")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        # Remove from all scan subscriptions
        for scan_id in list(self.scan_subscribers.keys()):
            self.scan_subscribers[scan_id].discard(websocket)
            if not self.scan_subscribers[scan_id]:
                del self.scan_subscribers[scan_id]
        logger.info(f"WebSocket disconnected: {len(self.active_connections)} active")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def send_to_scan_subscribers(self, scan_id: str, message: dict):
        """Send message to clients subscribed to specific scan"""
        if scan_id not in self.scan_subscribers:
            return
        
        disconnected = set()
        for connection in self.scan_subscribers[scan_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to scan subscriber: {e}")
                disconnected.add(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
            if scan_id in self.scan_subscribers:
                self.scan_subscribers[scan_id].discard(conn)
    
    def subscribe_to_scan(self, websocket: WebSocket, scan_id: str):
        """Subscribe client to specific scan updates"""
        if scan_id not in self.scan_subscribers:
            self.scan_subscribers[scan_id] = set()
        self.scan_subscribers[scan_id].add(websocket)
        logger.info(f"Client subscribed to scan {scan_id}: {len(self.scan_subscribers[scan_id])} subscribers")

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive messages from client (for future client→server commands)
            data = await websocket.receive_text()
            
            # Parse client commands
            try:
                import json
                message = json.loads(data)
                
                if message.get('type') == 'subscribe_scan':
                    scan_id = message.get('scan_id')
                    if scan_id:
                        manager.subscribe_to_scan(websocket, scan_id)
                        await websocket.send_json({
                            'type': 'subscribed',
                            'scan_id': scan_id
                        })
                
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Helper functions for broadcasting
async def broadcast_scan_progress(scan_id: int, progress: int, status: str, details: str = ""):
    """Broadcast scan progress update"""
    await manager.send_to_scan_subscribers(str(scan_id), {
        'type': 'scan_progress',
        'scan_id': scan_id,
        'progress': progress,  # 0-100
        'status': status,
        'details': details
    })

async def broadcast_scan_complete(scan_id: int, results: dict):
    """Broadcast scan completion"""
    await manager.send_to_scan_subscribers(str(scan_id), {
        'type': 'scan_complete',
        'scan_id': scan_id,
        'results': results
    })
    # Also broadcast to all clients
    await manager.broadcast({
        'type': 'scan_finished',
        'scan_id': scan_id,
        'summary': results.get('summary', {})
    })

async def broadcast_alert(alert: dict):
    """Broadcast security alert to all connected clients"""
    await manager.broadcast({
        'type': 'security_alert',
        'alert': alert,
        'timestamp': alert.get('timestamp', 'now')
    })

async def broadcast_threat_detected(threat_info: dict):
    """Broadcast immediate threat detection (high priority)"""
    await manager.broadcast({
        'type': 'threat_detected',
        'threat': threat_info,
        'priority': 'critical'
    })

# Initialize WebSocket with FastAPI app
def setup_websocket(app):
    """Add WebSocket router to FastAPI app"""
    app.include_router(router)
    logger.info("WebSocket endpoints registered")

# Example usage in scan workflow
"""
# In your scan execution code:
from api.websocket import broadcast_scan_progress, broadcast_scan_complete

# During scan:
await broadcast_scan_progress(scan.id, 25, 'scanning', 'Discovered 5 hosts...')

# After scan:
await broadcast_scan_complete(scan.id, {
    'hosts_discovered': 23,
    'vulnerabilities': 5,
    'summary': {...}
})
"""