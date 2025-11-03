from __future__ import annotations
import asyncio
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")

async def retry_async(func: Callable[[], Awaitable[T]], retries: int = 3, base_delay: float = 0.5, factor: float = 2.0,) -> T:
    attempt = 0
    last_exc: Exception | None = None
    while attempt <= retries:
        try:
            return await func()
        except Exception as e:
            last_exc = e
            if attempt == retries:
                raise
            delay = base_delay * (factor ** attempt)
            await asyncio.sleep(delay)
            attempt += 1
    
    assert last_exc is not None
    raise last_exc

