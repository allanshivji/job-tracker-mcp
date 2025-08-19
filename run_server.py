#!/usr/bin/env python3
"""
MCP Server startup script for job tracker
"""
import sys
import os
import signal
import asyncio
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

def signal_handler(signum, frame):
    """Handle shutdown signals with immediate exit"""
    logger.info(f"Received signal {signum}, shutting down immediately...")
    sys.exit(0)

def run_server():
    """Entry point with immediate signal handling"""
    try:
        # Add the project directory to Python path
        project_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_dir)
        logger.info(f"Project directory: {project_dir}")

        # Set environment variables
        os.environ['PYTHONPATH'] = project_dir
        logger.info("Environment variables set")
        
        # Set up signal handlers for immediate shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Starting MCP server...")
        
        # Import and run the server directly
        from src.server import main
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    run_server()