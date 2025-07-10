"""
Response compression middleware for better API performance
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import gzip
import json

class CompressionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, minimum_size: int = 1000):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Check if client accepts gzip
        accept_encoding = request.headers.get("accept-encoding", "")
        if "gzip" not in accept_encoding:
            return response
            
        # Only compress JSON responses above minimum size
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("application/json"):
            return response
            
        # Get response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
            
        # Only compress if body is large enough
        if len(body) < self.minimum_size:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        # Compress the response
        compressed_body = gzip.compress(body)
        
        # Update headers
        headers = dict(response.headers)
        headers["content-encoding"] = "gzip"
        headers["content-length"] = str(len(compressed_body))
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=headers,
            media_type=response.media_type
        )