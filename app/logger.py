import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": datetime.utcnow().isoformat(),
            "module": record.module,
            "function": record.funcName
        }
        return json.dumps(log)

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]

setup_logging()
