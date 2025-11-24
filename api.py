"""
CyberGuard Academy - FastAPI Backend

RESTful API for the CyberGuard Academy training platform.
Provides endpoints for session management, user actions, and evaluation results.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from loguru import logger

from main import get_orchestrator, CyberGuardOrchestrator
from cyberguard.models import (
    CyberGuardSession,
    UserRole,
    ThreatType,
    DifficultyLevel
)


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateSessionRequest(BaseModel):
    """Request to create a new training session."""
    user_id: str = Field(..., description="Anonymized user identifier")
    threat_type: str = Field(default="phishing", description="Type of threat scenario")
    difficulty: Optional[int] = Field(None, ge=1, le=5, description="Difficulty level (1-5)")
    user_role: str = Field(default="general", description="User's job function")


class CreateSessionResponse(BaseModel):
    """Response containing new session details."""
    session_id: str
    user_id: str
    scenario_type: str
    opening_narrative: str
    current_state: str
    difficulty_level: int


class UserActionRequest(BaseModel):
    """Request to process a user action during training."""
    session_id: str = Field(..., description="Active session ID")
    user_message: str = Field(..., description="User's input or action")
    action_type: str = Field(default="message", description="Type of action (message, click_link, report, etc.)")


class UserActionResponse(BaseModel):
    """Response to user action."""
    session_id: str
    narrative: str
    scenario_complete: bool = False
    hints_available: bool = True
    debrief: Optional[Dict[str, Any]] = None


class EvaluationResponse(BaseModel):
    """Complete evaluation and debrief for a session."""
    session_id: str
    overall_score: float
    risk_level: str
    component_scores: Dict[str, float]
    vulnerability_analysis: List[Dict[str, Any]]
    recommendations: List[str]
    duration_seconds: float
    completion_reason: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    agents_initialized: bool


# ============================================================================
# Lifecycle Management
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    # Startup
    logger.info("🚀 Starting CyberGuard Academy API")
    try:
        orchestrator = await get_orchestrator()
        logger.success("✅ API ready and all agents initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down CyberGuard Academy API")
    orchestrator = await get_orchestrator()
    await orchestrator.shutdown()
    logger.success("✅ API shutdown complete")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="CyberGuard Academy API",
    description="Multi-agent cybersecurity training platform with invisible assessment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CyberGuard Academy API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    try:
        orchestrator = await get_orchestrator()
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            agents_initialized=orchestrator.initialized
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/sessions", response_model=CreateSessionResponse, status_code=201)
async def create_session(request: CreateSessionRequest):
    """
    Create a new training session for a user.
    
    This endpoint initializes a new cybersecurity training scenario
    based on the user's profile and selected threat type.
    """
    try:
        orchestrator = await get_orchestrator()
        
        # Create session
        session = await orchestrator.create_session(
            user_id=request.user_id,
            threat_type=request.threat_type,
            difficulty=request.difficulty,
            user_role=request.user_role
        )
        
        # Extract opening narrative
        opening_narrative = ""
        if session.conversation_history:
            opening_narrative = session.conversation_history[0].get("content", "")
        
        logger.info(f"✅ Created session {session.session_id} for user {request.user_id}")
        
        return CreateSessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            scenario_type=session.scenario_type.value,
            opening_narrative=opening_narrative,
            current_state=session.current_state,
            difficulty_level=session.current_difficulty.value
        )
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@app.post("/sessions/action", response_model=UserActionResponse)
async def process_user_action(request: UserActionRequest):
    """
    Process a user action during a training scenario.
    
    This endpoint handles user interactions (messages, clicks, reports)
    and returns the Game Master's response and narrative progression.
    """
    try:
        orchestrator = await get_orchestrator()
        
        # Process action
        response = await orchestrator.process_user_action(
            session_id=request.session_id,
            user_message=request.user_message,
            action_type=request.action_type
        )
        
        logger.info(f"✅ Processed action for session {request.session_id}: {request.action_type}")
        
        return UserActionResponse(
            session_id=request.session_id,
            narrative=response.get("narrative", ""),
            scenario_complete=response.get("scenario_complete", False),
            hints_available=response.get("hints_available", True),
            debrief=response.get("debrief")
        )
        
    except ValueError as e:
        logger.warning(f"Invalid session: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process action: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process action: {str(e)}")


@app.post("/sessions/{session_id}/complete", response_model=EvaluationResponse)
async def complete_session(session_id: str, reason: str = "user_completion"):
    """
    Complete a training session and get evaluation results.
    
    This endpoint finalizes the scenario, triggers evaluation,
    and returns comprehensive learning analytics and debrief.
    """
    try:
        orchestrator = await get_orchestrator()
        
        # Complete scenario
        result = await orchestrator.complete_scenario(
            session_id=session_id,
            reason=reason
        )
        
        evaluation = result.get("evaluation", {})
        
        logger.info(f"✅ Completed session {session_id}")
        
        return EvaluationResponse(
            session_id=session_id,
            overall_score=evaluation.get("overall_score", 0.0),
            risk_level=evaluation.get("risk_level", "unknown"),
            component_scores=evaluation.get("component_scores", {}),
            vulnerability_analysis=evaluation.get("vulnerability_analysis", []),
            recommendations=evaluation.get("recommendations", []),
            duration_seconds=result.get("duration_seconds", 0.0),
            completion_reason=result.get("completion_reason", reason)
        )
        
    except ValueError as e:
        logger.warning(f"Invalid session: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to complete session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")


@app.get("/sessions/{session_id}", response_model=Dict[str, Any])
async def get_session(session_id: str):
    """
    Retrieve current state of a training session.
    
    Returns session details including conversation history,
    current state, and progress metrics.
    """
    try:
        orchestrator = await get_orchestrator()
        
        # Get session from active sessions or storage
        session = orchestrator.active_sessions.get(session_id)
        if not session:
            session = await orchestrator.session_manager.load_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "scenario_type": session.scenario_type.value,
            "current_state": session.current_state,
            "conversation_history": session.conversation_history,
            "difficulty_level": session.current_difficulty.value,
            "hints_used": session.hints_used,
            "duration_seconds": session.calculate_session_duration(),
            "is_complete": session.end_time is not None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")


@app.get("/user/{user_id}/profile", response_model=Dict[str, Any])
async def get_user_profile(user_id: str):
    """
    Retrieve user profile and learning analytics.
    
    Returns user's progress, vulnerability patterns,
    and performance history.
    """
    try:
        orchestrator = await get_orchestrator()
        
        # Load user profile
        profile = await orchestrator.user_profiler.load_profile(user_id)
        
        return profile
        
    except Exception as e:
        logger.error(f"Failed to retrieve user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")


# ============================================================================
# Development/Testing Endpoints
# ============================================================================

@app.get("/admin/active-sessions", response_model=List[str])
async def list_active_sessions():
    """List all active session IDs (admin/debug endpoint)."""
    try:
        orchestrator = await get_orchestrator()
        return list(orchestrator.active_sessions.keys())
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting CyberGuard Academy API server")
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
