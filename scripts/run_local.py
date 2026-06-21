"""Run all services locally for development."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import multiprocessing
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def run_api():
    """Run FastAPI server."""
    import uvicorn
    uvicorn.run(
        "src.api.routes:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


def run_dashboard():
    """Run Streamlit dashboard."""
    import subprocess
    subprocess.run([
        "streamlit", "run", "dashboard/app.py",
        "--server.port", "8501",
        "--server.headless", "true",
    ])


async def run_agents():
    """Run agent scheduler."""
    from src.scheduler.jobs import AgentScheduler
    scheduler = AgentScheduler()
    await scheduler.start()


def main():
    """Start all services."""
    logger.info("Starting Financial News Analyzer...")

    api_process = multiprocessing.Process(target=run_api, name="API Server")
    dashboard_process = multiprocessing.Process(target=run_dashboard, name="Dashboard")

    api_process.start()
    dashboard_process.start()

    logger.info("Services started:")
    logger.info("  - API: http://localhost:8000")
    logger.info("  - Dashboard: http://localhost:8501")
    logger.info("  - API Docs: http://localhost:8000/docs")

    try:
        api_process.join()
        dashboard_process.join()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        api_process.terminate()
        dashboard_process.terminate()


if __name__ == "__main__":
    main()