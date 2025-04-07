import time
import functools
import logging
from typing import Callable, Any

def timing_decorator(func_name: str = None):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            display_name = func_name or func.__name__
            execution_time = end_time - start_time
            logging.info(f"{display_name} 执行时间: {execution_time:.2f} 秒")
            return result
        return wrapper
    return decorator