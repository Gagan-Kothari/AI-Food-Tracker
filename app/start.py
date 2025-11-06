#!/usr/bin/env python3
"""
Startup script for Railway deployment
Reads PORT from environment variable and starts uvicorn
"""
import os
import sys

# Add parent directory to path so "app" imports work
# When running from app/ directory, we need parent in path for "from app.xxx" imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import uvicorn

if __name__ == "__main__":
    # Get PORT from environment variable, default to 8000
    port = int(os.getenv("PORT", "8000"))
    
    # Start the FastAPI application
    # Use "app.main:app" because we added parent to path
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

