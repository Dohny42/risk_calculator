import time
import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start = time.perf_counter()

        with logger.contextualize(request_id=request_id):
            response: Response | None = None
            try:
                response = await call_next(request)
                return response
            finally:
                duration_ms = round((time.perf_counter() - start) * 1000, 2)
                status = response.status_code if response is not None else 500
                logger.bind(
                    method=request.method,
                    path=request.url.path,
                    status_code=status,
                    duration_ms=duration_ms,
                ).info("request_finished")

                if response is not None:
                    response.headers["X-Request-ID"] = request_id
