# utils/retry.py
"""
Retry decorator with exponential backoff.
- Works for both synchronous and asynchronous functions
- Backward-compatible param names: (max_attempts / retries) and (delay_seconds / delay)
- Optional jitter and custom logger
"""

from __future__ import annotations

import asyncio
import functools
import logging
import random
import time
from typing import Callable, Optional, Tuple, Type, Union
from utils.logger import get_logger
logger = get_logger(__name__)

ExceptionTypes = Union[Type[BaseException], Tuple[Type[BaseException], ...]]


def retry(
    # Backward-compatible aliases:
    retries: Optional[int] = None,
    max_attempts: int = 3,
    delay: Optional[float] = None,
    delay_seconds: float = 1.0,
    # Standard knobs:
    backoff: float = 2.0,
    exceptions: ExceptionTypes = (Exception,),
    jitter: float = 0.0,  # adds up to ±jitter seconds to each delay
    logger: Optional[logging.Logger] = None,
):
    """
    Decorate a function to retry on specific exceptions with exponential backoff.

    Args:
        retries: Alias for max_attempts (kept for compatibility).
        max_attempts: Total number of retry attempts before giving up.
        delay: Alias for delay_seconds (kept for compatibility).
        delay_seconds: Initial delay in seconds before the first retry.
        backoff: Multiplier applied to the delay after each failure.
        exceptions: Exception class (or tuple of classes) that triggers a retry.
        jitter: If > 0, adds small random noise to delay to avoid thundering herd.
        logger: Optional logger; defaults to root logger if not provided.
    """
    attempts = retries if retries is not None else max_attempts
    initial_delay = delay if delay is not None else delay_seconds
    log = logger or logging.getLogger(__name__)

    # Normalize exceptions to a tuple
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    def _sleep_with_jitter(seconds: float, is_async: bool):
        # Compute jittered sleep time
        if jitter and jitter > 0:
            # jitter in [-jitter, +jitter]
            seconds = max(0.0, seconds + random.uniform(-jitter, jitter))
        if is_async:
            return asyncio.sleep(seconds)
        else:
            time.sleep(seconds)
            return None

    def decorator(func: Callable):
        # Async wrapper
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                delay_now = initial_delay
                for attempt_idx in range(1, attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt_idx >= attempts:
                            log.error(
                                "Final async attempt %s failed for %s: %s",
                                attempt_idx, func.__name__, e
                            )
                            raise
                        log.warning(
                            "Async attempt %s failed for %s: %s. Retrying in %.2fs...",
                            attempt_idx, func.__name__, e, delay_now
                        )
                        await _sleep_with_jitter(delay_now, is_async=True)
                        delay_now *= backoff

            return async_wrapper

        # Sync wrapper
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            delay_now = initial_delay
            for attempt_idx in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt_idx >= attempts:
                        log.error(
                            "Final attempt %s failed for %s: %s",
                            attempt_idx, func.__name__, e
                        )
                        raise
                    log.warning(
                        "Attempt %s failed for %s: %s. Retrying in %.2fs...",
                        attempt_idx, func.__name__, e, delay_now
                    )
                    _sleep_with_jitter(delay_now, is_async=False)
                    delay_now *= backoff

        return sync_wrapper

    return decorator
