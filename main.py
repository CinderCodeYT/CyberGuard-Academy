"""
CyberGuard Academy - Main Entry Point

This module serves as the primary entry point for the application.
It provides the global orchestrator instance and CLI startup capabilities.
"""

import asyncio
from typing import Optional
from loguru import logger
import uvicorn

from cyberguard.orchestrator import CyberGuardOrchestrator

# Module-level orchestrator instance
_orchestrator: Optional[CyberGuardOrchestrator] = None


async def get_orchestrator() -> CyberGuardOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = CyberGuardOrchestrator()
        await _orchestrator.initialize()
    
    return _orchestrator


def main():
    """Main entry point to start the API server."""
    logger.info("🎯 Starting CyberGuard Academy")
    
    try:
        # Run the API server directly
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
