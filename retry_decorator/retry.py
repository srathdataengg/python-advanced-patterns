"""
We have an API that sometime fails due to network issues. We don't want to immediately retry,
because that can overload the service. Can you write a Python decorator that automatically retries
a function call with exponential backoff, works for both synchronous functions and lets us configure retries,
delay and exception types?
"""

import time
import asyncio
import logging
import functools
from typing import Callable, Type, Tuple, Union

logging.basicConfig(level=logging.INFO, format="%(asctime)s[%(levelname)s] %(message)s")

def retry(
        retries: int = 3,
        delay: float = 1,
        backoff: float =2,
        exceptions: Union[Type[Exception],Tuple[Type[Exception],...]] = Exception,
):
    """
    Retry decorator  with exponential backoff.

    Args:
        :param retries (int): Number of retry attempts
        :param delay: Initial delay between retries in seconds.
        :param backoff: Multiplication factor for delay after each failure.
        :param exceptions (Exception or tuple): Exceptions(s) to trigger a retry
        :return:
    """

    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            """ Async version """
    @functools.wraps(func)
    async def async_wrapper(*args,**kwargs):
        _delay = delay
        for attempt in range(1, retries + 2 ): # retries + 1 final attempt
            try:
                return await func(*args,**kwargs)
            except exceptions as e:
                if attempt > retries:
                    logging.error(f"Final attempt failed:{e} ")
                    raise
                logging.warning(f"Async attempt {attempt} failed: {e}. Retrying in {_delay:.2f}s...")
                await asyncio.sleep(_delay)
                _delay *=backoff
    return async_wrapper


