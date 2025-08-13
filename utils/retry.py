import time
import functools


from utils.logger import logger

logging = logger.warning("This is a warning")


def retry(max_attempts=3, delay_seconds=2, exceptions=(Exception,)):
    """
    A decorator to automatically retry a function if it fails.

    Args:
    :param max_attempts : How many times to retry before giving up.
    :param delay_seconds: How many seconds to wait between retries.
    :param exceptions: Tuple of exception types to catch and retry on
    :return:
    """

    def decorator(func):
        @functools.wraps(func) # Preserves original function's name and docstring
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    logger.warning(
                        f"Attempt {attempts} failed for{func.__name__} with error: {e}"
                    )
                    if attempts == max_attempts:
                        logger.error(f"All {max_attempts} attempts failed.")
                        raise
                    time.sleep(delay_seconds)

        return wrapper
    return decorator
