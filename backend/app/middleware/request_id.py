import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request
from starlette.responses import Response

from app.core.request_context import TRACE_ID_HEADER, reset_trace_id, set_trace_id

logger = logging.getLogger(__name__)


async def request_id_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    trace_id = request.headers.get(TRACE_ID_HEADER) or str(uuid4())
    request.state.trace_id = trace_id
    token = set_trace_id(trace_id)

    try:
        response = await call_next(request)
        if response.status_code >= 400:
            logger.warning(
                "event=api_error trace_id=%s method=%s path=%s status_code=%s",
                trace_id,
                request.method,
                request.url.path,
                response.status_code,
            )
        response.headers[TRACE_ID_HEADER] = trace_id
        return response
    except Exception:
        logger.exception(
            "event=api_error trace_id=%s method=%s path=%s status_code=500",
            trace_id,
            request.method,
            request.url.path,
        )
        raise
    finally:
        reset_trace_id(token)
