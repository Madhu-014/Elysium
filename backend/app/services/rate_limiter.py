from collections import defaultdict, deque
from threading import Lock
from time import time

from fastapi import HTTPException, Request, status

from app.config import settings

_WINDOW_SECONDS = 60.0
_hits_by_ip: dict[str, deque[float]] = defaultdict(deque)
_lock = Lock()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def enforce_ip_rate_limit(request: Request) -> None:
    if not settings.rate_limit_enabled:
        return

    now = time()
    window_start = now - _WINDOW_SECONDS
    ip = _client_ip(request)
    limit = max(settings.rate_limit_requests_per_minute, 1)

    with _lock:
        hits = _hits_by_ip[ip]
        while hits and hits[0] < window_start:
            hits.popleft()

        if len(hits) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for IP {ip}. Limit: {limit} requests per minute.",
            )

        hits.append(now)


def clear_rate_limit_state() -> None:
    with _lock:
        _hits_by_ip.clear()
