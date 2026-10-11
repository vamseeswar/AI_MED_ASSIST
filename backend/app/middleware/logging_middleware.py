import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from backend.app.core.logging import app_logger, redact_sensitive_data


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method

        # Log incoming request (excluding health checks to prevent spam if desired, but good for auditing)
        if not path.endswith("/health"):
            app_logger.info(
                f"Incoming request: {method} {path} from {client_host}"
            )

        try:
            response: Response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            if not path.endswith("/health"):
                app_logger.info(
                    f"Completed request: {method} {path} status={response.status_code} in {duration_ms:.2f}ms"
                )
            return response
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            app_logger.error(
                f"Request failed: {method} {path} error={str(exc)} in {duration_ms:.2f}ms"
            )
            raise exc
