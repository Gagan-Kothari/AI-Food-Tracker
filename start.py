#!/usr/bin/env python3
"""
Startup script for Railway deployment
Reads PORT from environment variable and starts uvicorn
"""
import os
import uvicorn

if __name__ == "__main__":
    # Get PORT from environment variable, default to 8000
    port = int(os.getenv("PORT", "8000"))
    
    # Start the FastAPI application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

