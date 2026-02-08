"""
Rate limiting middleware for the chatbot API endpoints.
"""

import time
from collections import defaultdict, deque
from typing import Dict
from fastapi import Request, HTTPException, status
from functools import wraps


class RateLimiter:
    """
    Simple rate limiter that tracks requests by IP address.
    """

    def __init__(self, max_requests: int = 10, window_size: int = 60):
        """
        Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed per window
            window_size: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests: Dict[str, deque] = defaultdict(deque)

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request from the given identifier is allowed.

        Args:
            identifier: Identifier for the requester (e.g., IP address)

        Returns:
            bool: True if request is allowed, False otherwise
        """
        current_time = time.time()

        # Clean up old requests outside the window
        while (self.requests[identifier] and
               current_time - self.requests[identifier][0] > self.window_size):
            self.requests[identifier].popleft()

        # Check if we're under the limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True

        return False


# Create a global rate limiter instance
chat_rate_limiter = RateLimiter(max_requests=30, window_size=60)  # 30 requests per minute per IP


def rate_limit(max_requests: int = 30, window_size: int = 60):
    """
    Decorator for rate limiting specific endpoints.

    Args:
        max_requests: Maximum number of requests allowed per window
        window_size: Time window in seconds
    """
    limiter = RateLimiter(max_requests, window_size)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or args (depends on FastAPI's injection)
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            if request:
                client_ip = request.client.host if request.client else "unknown"
                if not limiter.is_allowed(client_ip):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded"
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_rate_limit(request: Request) -> bool:
    """
    Check if the current request is within the rate limit.

    Args:
        request: FastAPI request object

    Returns:
        bool: True if request is allowed, raises HTTPException if not
    """
    client_ip = request.client.host if request.client else "unknown"

    if not chat_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )

    return True