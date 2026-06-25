#!/usr/bin/env python3
"""
Sentinel Prime API Error Handling Standardization
Standardized error responses, validation middleware, and user-friendly messages.

Created by: Alex Kumar (Lead Developer)
Ticket: TICKET-0005
"""

from fastapi import HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sentinel-api-errors')

class SentinelAPIError(HTTPException):
    """Base class for all Sentinel Prime API errors."""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        
        super().__init__(
            status_code=status_code,
            detail={
                "error": error_code,
                "message": message,
                "details": self.details
            }
        )

# ============================================================================
# Specific Error Classes
# ============================================================================

class ValidationError(SentinelAPIError):
    """422 Unprocessable Entity - Validation failed."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details
        )

class BadRequestError(SentinelAPIError):
    """400 Bad Request - Invalid input."""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            message=message,
            details=details
        )

class NotFoundError(SentinelAPIError):
    """404 Not Found - Resource doesn't exist."""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
            details={"resource": resource, "resource_id": resource_id}
        )

class SecurityError(SentinelAPIError):
    """403 Forbidden - Security violation detected."""
    
    def __init__(self, message: str, log_attempt: bool = True):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="SECURITY_VIOLATION",
            message=message,
            details={"logged": log_attempt}
        )
        
        if log_attempt:
            logger.warning(f"🚨 Security violation: {message}")

class RateLimitError(SentinelAPIError):
    """429 Too Many Requests - Rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message="Too many requests. Please slow down.",
            details={"retry_after_seconds": retry_after}
        )

class InternalError(SentinelAPIError):
    """500 Internal Server Error - Unexpected error."""
    
    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message=message,
            details={}
        )
        logger.error(f"💥 Internal error: {message}")

# ============================================================================
# Validation Helpers
# ============================================================================

def validate_ip_address(ip: str) -> str:
    """Validate IP address format."""
    import re
    
    if not ip:
        raise BadRequestError("IP address cannot be empty")
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        octets = ip.split('.')
        if all(0 <= int(o) <= 255 for o in octets):
            return ip
    
    # CIDR notation
    cidr_pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if re.match(cidr_pattern, ip):
        ip_part, prefix = ip.split('/')
        if 0 <= int(prefix) <= 32:
            return validate_ip_address(ip_part)
    
    raise BadRequestError(
        f"Invalid IP address format: {ip}",
        details={"expected": "IPv4 (e.g., 192.168.0.1) or CIDR (e.g., 192.168.0.1/24)"}
    )

def validate_scan_type(scan_type: str) -> str:
    """Validate scan type."""
    valid_types = ['ping', 'syn', 'connect', 'udp', 'fin', 'null', 'xmas']
    
    if not scan_type:
        raise BadRequestError("Scan type cannot be empty")
    
    if scan_type.lower() not in valid_types:
        raise BadRequestError(
            f"Invalid scan type: {scan_type}",
            details={
                "valid_types": valid_types,
                "provided": scan_type
            }
        )
    
    return scan_type.lower()

def validate_port(port: int) -> int:
    """Validate port number."""
    if not isinstance(port, int) or not (1 <= port <= 65535):
        raise BadRequestError(
            f"Invalid port number: {port}",
            details={"valid_range": "1-65535"}
        )
    return port

# ============================================================================
# Exception Handlers
# ============================================================================

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with user-friendly messages."""
    
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error['loc'])
        msg = error['msg']
        errors.append({"field": field, "message": msg})
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": {
                "errors": errors,
                "path": request.url.path
            }
        }
    )

async def sentinel_exception_handler(request: Request, exc: SentinelAPIError):
    """Handle Sentinel custom exceptions."""
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions gracefully."""
    
    logger.error(f"💥 Unexpected error on {request.url.path}: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {
                "type": type(exc).__name__,
                "path": request.url.path
            }
        }
    )

# ============================================================================
# Middleware
# ============================================================================

class ErrorLoggingMiddleware:
    """Middleware to log all errors with context."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        from starlette.responses import JSONResponse
        
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        
        try:
            return await self.app(scope, receive, send)
        except SentinelAPIError as exc:
            response = JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.error_code,
                    "message": exc.message,
                    "details": exc.details
                }
            )
            await response(scope, receive, send)
        except Exception as exc:
            logger.error(f"Unhandled exception: {exc}")
            raise

# ============================================================================
# Example Usage in Routes
# ============================================================================

"""
Example integration in FastAPI routes:

from fastapi import FastAPI, Depends
from core.error_handling import (
    BadRequestError,
    NotFoundError,
    ValidationError,
    validate_ip_address,
    validate_scan_type
)

app = FastAPI()

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SentinelAPIError, sentinel_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.post("/scans/network")
async def create_network_scan(target: str, scan_type: str):
    # Validate inputs using standardized validators
    valid_target = validate_ip_address(target)
    valid_scan_type = validate_scan_type(scan_type)
    
    # Business logic here
    if valid_target == "192.168.0.1":
        raise BadRequestError("Cannot scan the gateway")
    
    return {"status": "started", "target": valid_target}

@app.get("/devices/{device_id}")
async def get_device(device_id: str):
    device = get_device_from_db(device_id)
    
    if not device:
        raise NotFoundError("Device", device_id)
    
    return device
"""

print("✅ Error handling module created")
print("   Features:")
print("   - 6 standardized error classes")
print("   - 3 validation helper functions")
print("   - 3 exception handlers")
print("   - Error logging middleware")
print("   - User-friendly error messages")
print("   - Consistent error response format")