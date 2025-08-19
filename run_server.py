#!/usr/bin/env python3
"""
MCP Server startup script for job tracker
"""
import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/job_tracker_mcp.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

try:
    # Add the project directory to Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    logger.info(f"Project directory: {project_dir}")

    # Set environment variables
    os.environ['PYTHONPATH'] = project_dir
    logger.info("Environment variables set")

    # Import and run the server
    from src.server import main
    import asyncio
    
    logger.info("Starting MCP server...")
    asyncio.run(main())
    
except Exception as e:
    logger.error(f"Error starting server: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)