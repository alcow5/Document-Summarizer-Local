"""
Middleware for Privacy-Focused AI Document Summarizer
Provides security and rate limiting functionality
"""

import time
from collections import defaultdict
from typing import Dict, Any, Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for API protection"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with security headers"""
        try:
            # Log request (without sensitive data)
            logger.debug(f"Request: {request.method} {request.url.path}")
            
            # Validate request method
            if request.method not in ["GET", "POST", "DELETE", "OPTIONS"]:
                return JSONResponse(
                    status_code=405,
                    content={"detail": "Method not allowed"}
                )
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            # Add custom headers
            response.headers["X-API-Version"] = "1.0.0"
            response.headers["X-Privacy-Mode"] = "local-only"
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent abuse"""
    
    def __init__(self, app, config: Dict[str, Any] = None, **kwargs):
        super().__init__(app)
        self.config = config or {}
        self.api_config = self.config.get("api", {})
        
        # Rate limiting settings
        self.max_requests = self.api_config.get("rate_limit_requests", 100)
        self.window_minutes = self.api_config.get("rate_limit_window_minutes", 15)
        self.window_seconds = self.window_minutes * 60
        
        # Storage for rate limit tracking
        self.request_counts = defaultdict(list)
        self.blocked_ips = {}  # IP -> block_until_timestamp
        
        # Whitelist localhost for development
        self.whitelist = ["127.0.0.1", "localhost", "::1"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""
        try:
            client_ip = self._get_client_ip(request)
            
            # Skip rate limiting for whitelisted IPs
            if client_ip in self.whitelist:
                return await call_next(request)
            
            # Check if IP is currently blocked
            if self._is_blocked(client_ip):
                logger.warning(f"Blocked request from rate-limited IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please try again later.",
                        "retry_after": self._get_retry_after(client_ip)
                    }
                )
            
            # Check rate limit
            if self._is_rate_limited(client_ip):
                self._block_ip(client_ip)
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please try again later.",
                        "retry_after": self.window_seconds
                    }
                )
            
            # Record request
            self._record_request(client_ip)
            
            # Process request
            response = await call_next(request)
            
            # Add rate limit headers
            remaining = max(0, self.max_requests - len(self.request_counts[client_ip]))
            response.headers["X-RateLimit-Limit"] = str(self.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Window"] = str(self.window_seconds)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limit middleware error: {e}")
            return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_blocked(self, client_ip: str) -> bool:
        """Check if IP is currently blocked"""
        if client_ip not in self.blocked_ips:
            return False
        
        block_until = self.blocked_ips[client_ip]
        current_time = time.time()
        
        if current_time >= block_until:
            # Block expired, remove from blocked list
            del self.blocked_ips[client_ip]
            return False
        
        return True
    
    def _get_retry_after(self, client_ip: str) -> int:
        """Get seconds until IP is unblocked"""
        if client_ip not in self.blocked_ips:
            return 0
        
        block_until = self.blocked_ips[client_ip]
        current_time = time.time()
        
        return max(0, int(block_until - current_time))
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if IP has exceeded rate limit"""
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Clean old requests
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if req_time > window_start
            ]
        
        # Check if limit exceeded
        request_count = len(self.request_counts[client_ip])
        return request_count >= self.max_requests
    
    def _record_request(self, client_ip: str):
        """Record a request timestamp for IP"""
        current_time = time.time()
        self.request_counts[client_ip].append(current_time)
    
    def _block_ip(self, client_ip: str):
        """Block IP for extended period"""
        block_duration = self.window_seconds * 2  # Block for twice the window
        self.blocked_ips[client_ip] = time.time() + block_duration
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        current_time = time.time()
        
        # Count active IPs
        active_ips = 0
        total_requests = 0
        
        for ip, requests in self.request_counts.items():
            window_start = current_time - self.window_seconds
            recent_requests = [req for req in requests if req > window_start]
            
            if recent_requests:
                active_ips += 1
                total_requests += len(recent_requests)
        
        # Count blocked IPs
        blocked_count = sum(
            1 for block_until in self.blocked_ips.values()
            if block_until > current_time
        )
        
        return {
            "active_ips": active_ips,
            "total_recent_requests": total_requests,
            "blocked_ips": blocked_count,
            "rate_limit": self.max_requests,
            "window_minutes": self.window_minutes
        }


class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging middleware"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log requests and responses"""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"({process_time:.3f}s) "
            f"{request.method} {request.url.path}"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = str(round(process_time, 3))
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle uncaught exceptions"""
        try:
            return await call_next(request)
        except HTTPException:
            # Re-raise HTTP exceptions (they're handled by FastAPI)
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unhandled error in {request.method} {request.url.path}: {e}")
            
            # Return generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An unexpected error occurred",
                    "error_id": str(int(time.time()))  # Simple error ID for tracking
                }
            ) 