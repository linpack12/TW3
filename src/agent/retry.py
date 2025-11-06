from __future__ import annotations
import asyncio
from typing import Awaitable, Callable, TypeVar

# Keeps return type from func()
T = TypeVar("T")

""" 
Retry an async function with exponential backoff, return result of func() if successful,
otherwise re raises the last exception
"""
async def retry_async(func: Callable[[], Awaitable[T]], retries: int = 3, base_delay: float = 0.5, factor: float = 2.0,) -> T:
    attempt = 0
    last_exc: Exception | None = None
    while attempt <= retries:
        try:
            return await func() # Try executing the async function
        except Exception as e:
            last_exc = e
            if attempt == retries:
                raise
            delay = base_delay * (factor ** attempt)
            await asyncio.sleep(delay)
            attempt += 1
    
    assert last_exc is not None
    raise last_exc

