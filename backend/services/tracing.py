from functools import lru_cache
from typing import Any

from backend.config import settings


@lru_cache(maxsize=1)
def _build_handler():
    """Build a Langfuse LangChain callback handler. Returns None if not configured."""
    if not settings.LANGFUSE_SECRET_KEY:
        return None
    try:
        from langfuse.callback import CallbackHandler
        return CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
        )
    except Exception:
        return None


def get_tracer_config(trace_name: str = "") -> dict[str, Any]:
    """Return a LangChain runnable config dict that injects Langfuse tracing if configured.

    Usage::
        result = await chain.ainvoke(inputs, config=get_tracer_config("supervisor"))
    """
    handler = _build_handler()
    if handler is None:
        return {}
    try:
        # Each invocation should get a fresh span — clone the handler with a new trace
        from langfuse.callback import CallbackHandler
        span_handler = CallbackHandler(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            host=settings.LANGFUSE_HOST,
            trace_name=trace_name or "opsmind-agent",
        )
        return {"callbacks": [span_handler]}
    except Exception:
        return {}


def langfuse_enabled() -> bool:
    return bool(settings.LANGFUSE_SECRET_KEY)
