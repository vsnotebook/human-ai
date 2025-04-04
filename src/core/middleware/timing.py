from fastapi import Request
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Path: {request.url.path} | Method: {request.method} | Processing time: {process_time:.2f}ms")
    return response