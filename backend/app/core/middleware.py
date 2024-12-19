from fastapi import Request
import time
import logging
from typing import Callable
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next: Callable):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Логируем информацию о запросе
    process_time = time.time() - start_time
    log_dict = {
        "path": request.url.path,
        "method": request.method,
        "process_time": f"{process_time:.2f}s",
        "status_code": response.status_code
    }
    
    if response.status_code >= 400:
        logger.error(json.dumps(log_dict))
    else:
        logger.info(json.dumps(log_dict))
    
    return response