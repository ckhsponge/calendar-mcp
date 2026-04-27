"""
Single entry point for supergateway.
- Starts FastAPI (uvicorn) in a background thread immediately
- Starts MCP stdio server in the foreground right away
- MCP responds to initialize/ping instantly; tools wait for FastAPI lazily on first call
"""
import os
import sys
import logging
import logging.config
import threading
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
        'stderr': {
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
    'root': {'handlers': ['stderr', 'file'], 'level': 'INFO'},
    'loggers': {
        'uvicorn.error': {'level': 'INFO', 'handlers': ['stderr', 'file'], 'propagate': False},
        'uvicorn.access': {'level': 'WARNING', 'handlers': ['stderr', 'file'], 'propagate': False},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def run_fastapi():
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8001))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    logger.info(f"Starting FastAPI on {host}:{port}")
    uvicorn.run("src.server:app", host=host, port=port, reload=reload, log_config=LOGGING_CONFIG)


if __name__ == "__main__":
    # Start FastAPI in background immediately — don't wait for it
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    # Remove stderr handler so MCP stdio stays clean
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)

    # Start MCP stdio server immediately — responds to initialize/ping right away
    from src.mcp_bridge import create_mcp_server
    mcp = create_mcp_server()
    logger.info("Starting MCP stdio server")
    mcp.run(transport='stdio')
