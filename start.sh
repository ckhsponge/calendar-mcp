#!/bin/bash
# Start FastAPI in the background
python run_api.py &

# Hand off to MCP stdio server (foreground, supergateway talks to this)
exec python run_mcp.py
