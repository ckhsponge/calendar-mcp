"""
Standalone MCP stdio server entry point.
Run this as the stdio child process for supergateway (or any MCP client).
FastAPI must be running separately (see run_api.py).
"""
import os
import sys
import logging
import logging.config
from dotenv import load_dotenv

load_dotenv()

project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

log_file_path = os.path.join(project_dir, 'calendar_mcp.log')

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'},
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': log_file_path,
            'mode': 'a',
            'formatter': 'default',
        },
    },
    'root': {'handlers': ['file'], 'level': 'INFO'},
})

logger = logging.getLogger(__name__)
logger.info("MCP stdio server starting")

from src.mcp_bridge import create_mcp_server

mcp = create_mcp_server()
logger.info("Starting MCP server with stdio transport")
mcp.run(transport='stdio')
