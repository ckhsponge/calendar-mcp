"""
Standalone FastAPI server entry point.
Run this separately from the MCP server (see run_mcp.py).
"""
import os
import sys
import logging
import logging.config
import uvicorn
from dotenv import load_dotenv

load_dotenv()

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

os.environ["PYTHONPATH"] = f"{project_dir}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"

log_file_path = os.path.join(project_dir, 'calendar_mcp.log')

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': log_file_path,
            'mode': 'a',
            'formatter': 'default',
        },
    },
    'root': {'handlers': ['console', 'file'], 'level': 'INFO'},
    'loggers': {
        'uvicorn.error': {'level': 'INFO', 'handlers': ['console', 'file'], 'propagate': False},
        'uvicorn.access': {'level': 'WARNING', 'handlers': ['console', 'file'], 'propagate': False},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", 8001))
reload = os.getenv("RELOAD", "false").lower() == "true"

logger.info(f"Starting FastAPI server on {host}:{port}")

uvicorn.run(
    "src.server:app",
    host=host,
    port=port,
    reload=reload,
    log_config=LOGGING_CONFIG,
)
