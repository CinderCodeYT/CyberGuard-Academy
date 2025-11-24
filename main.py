"""
CyberGuard Academy - Main Orchestration System

This is the main entry point for the CyberGuard Academy training platform.
It coordinates the full scenario lifecycle:
1. Initialize all agents (Game Master, Threat Actors, Evaluation, Memory)
2. Set up session management
3. Execute complete training scenarios
4. Provide results and debrief

This serves as both a standalone orchestrator and the backend for the API layer.
"""

import asyncio
import sys
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from loguru import logger

# Core imports
from cyberguard.config import settings
from cyberguard.models import (
    CyberGuardSession,
    ScenarioContext,
    UserRole,
    DifficultyLevel,
    ThreatType,
    SocialEngineeringPattern,
    DecisionPoint,
    AgentMessage
)

# Agent imports
from agents.game_master.game_master import GameMasterAgent
from agents.threat_actors.phishing import PhishingAgent
from agents.evaluation.evaluation_agent import EvaluationAgent
from agents.memory.memory_manager import MemoryManagerAgent

# Tool imports
from tools.session_manager import SessionManager
from tools.user_profiler import UserProfiler


class CyberGuardOrchestrator:
    """
    Main orchestrator for CyberGuard Academy training platform.
    
    Manages the complete lifecycle of cybersecurity training scenarios:
    - Agent initialization and coordination
    - Session creation and management
    - Scenario execution flow
    - Evaluation and debrief generation
    """
    
    def __init__(self):
        """Initialize the orchestrator and all agents."""
        logger.info("🚀 Initializing CyberGuard Academy Orchestrator")
        
        # Initialize agents
        self.game_master = GameMasterAgent()
        self.phishing_agent = PhishingAgent()
        self.evaluation_agent = EvaluationAgent()
        self.memory_manager = MemoryManagerAgent()
        
        # Initialize tools
        self.session_manager = SessionManager()
        self.user_profiler = UserProfiler()
        
        # System state
        self.initialized = False
        self.active_sessions: Dict[str, CyberGuardSession] = {}
        
    async def initialize(self) -> None:
        """Initialize all agents and tools."""
        if self.initialized:
            logger.warning("Orchestrator already initialized")
            return
        
        logger.info("Initializing all agents...")
        
        try:
            # Initialize agents in parallel for efficiency
            await asyncio.gather(
                self.game_master.initialize(),
                self.phishing_agent.initialize(),
                self.evaluation_agent.initialize(),
                self.memory_manager.initialize()
            )
            
            # Initialize tools
            await self.session_manager.initialize()
            await self.user_profiler.initialize()
            
            self.initialized = True
            logger.success("✅ All agents and tools initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all agents and complete active sessions."""
        logger.info("🛑 Shutting down CyberGuard Academy Orchestrator")
        
        if not self.initialized:
            return
        
        try:
            # Complete all active sessions
            for session_id in list(self.active_sessions.keys()):
                logger.info(f"Completing active session: {session_id}")
                await self.complete_scenario(session_id, reason="system_shutdown")
            
            # Shutdown agents in parallel
            await asyncio.gather(
                self.game_master.shutdown(),
                self.phishing_agent.shutdown(),
                self.evaluation_agent.shutdown(),
                self.memory_manager.shutdown()
            )
            
            # Shutdown tools
            await self.session_manager.shutdown()
            await self.user_profiler.shutdown()
            
            self.initialized = False
            logger.success("✅ Orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
            raise
    
    async def create_session(
        self,
        user_id: str,
        threat_type: str = "phishing",
        difficulty: Optional[int] = None,
        user_role: str = "general"
    ) -> CyberGuardSession:
        """
        Create a new training session for a user.
        
        Args:
            user_id: Anonymized user identifier
            threat_type: Type of threat scenario (phishing, vishing, etc.)
            difficulty: Optional difficulty override (1-5)
            user_role: User's job function for personalization
            
        Returns:
            Newly created CyberGuardSession
        """
        logger.info(f"Creating new session for user {user_id}: {threat_type}")
        
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")
        
        # Load user profile for personalization
        user_profile = await self.user_profiler._load_profile(user_id)
        
        # Handle case where profile doesn't exist yet (new user)
        if user_profile is None:
            user_profile = {
                "user_id": user_id,
                "current_difficulty": settings.default_difficulty_level,
                "recent_patterns": [],
                "vulnerability_areas": []
            }
        
        # Determine difficulty level (use profile or provided value)
        if difficulty is None:
            difficulty = user_profile.get("current_difficulty", settings.default_difficulty_level)
        
        # Create scenario context
        context = ScenarioContext(
            user_role=UserRole(user_role),
            difficulty_level=DifficultyLevel(difficulty),
            threat_pattern=SocialEngineeringPattern.URGENCY,  # Will be selected by Game Master
            recently_seen_patterns=user_profile.get("recent_patterns", []),
            vulnerability_areas=user_profile.get("vulnerability_areas", [])
        )
        
        # Start scenario via Game Master
        session = await self.game_master.start_scenario(
            user_id=user_id,
            scenario_type=threat_type,
            context=context
        )
        
        # Store session
        self.active_sessions[session.session_id] = session
        await self.session_manager.save_session(session)
        
        # Notify evaluation agent of new session
        await self._notify_evaluation_agent("session_started", session)
        
        logger.success(f"✅ Session {session.session_id} created successfully")
        return session
    
    async def process_user_action(
        self,
        session_id: str,
        user_message: str,
        action_type: str = "message"
    ) -> Dict[str, Any]:
        """
        Process a user action during a training scenario.
        
        Args:
            session_id: ID of the active session
            user_message: User's input/action
            action_type: Type of action (message, click_link, report_phishing, etc.)
            
        Returns:
            Response containing narrative, feedback, and next steps
        """
        logger.info(f"Processing user action in session {session_id}: {action_type}")
        
        # Retrieve session
        session = self.active_sessions.get(session_id)
        if not session:
            # Try loading from storage
            session = await self.session_manager.load_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            self.active_sessions[session_id] = session
        
        # Add user message to conversation history
        session.add_message("user", user_message)
        
        # Track decision point for evaluation
        decision_point = DecisionPoint(
            turn=len(session.conversation_history),
            vulnerability=session.scenario_type.value,
            user_choice=action_type,
            correct_choice="",  # Will be determined by evaluation agent
            risk_score_impact=0.0  # Will be calculated by evaluation agent
        )
        session.record_decision(decision_point)
        
        # Process through Game Master
        response = await self.game_master.handle_user_response(
            session_id=session.session_id,
            user_input=user_message
        )
        
        # Extract narrative from response
        narrative = response.get("content", response.get("narrative", ""))
        
        # Add Game Master response to conversation (only if not already added by handle_user_response)
        if narrative and session.conversation_history[-1]["content"] != narrative:
            session.add_message("game_master", narrative)
        
        # Update response to use 'narrative' key for API compatibility
        response["narrative"] = narrative
        
        # Send decision to evaluation agent (invisible assessment)
        await self._notify_evaluation_agent("decision_made", session, decision_point)
        
        # Update session storage
        await self.session_manager.save_session(session)
        
        # Check if scenario is complete
        if response.get("scenario_complete", False):
            logger.info(f"Scenario complete for session {session_id}")
            await self.complete_scenario(session_id)
            response["debrief"] = await self._generate_debrief(session)
        
        return response
    
    async def complete_scenario(
        self,
        session_id: str,
        reason: str = "normal_completion"
    ) -> Dict[str, Any]:
        """
        Complete a training scenario and generate evaluation/debrief.
        
        Args:
            session_id: ID of the session to complete
            reason: Reason for completion (normal_completion, timeout, user_exit, system_shutdown)
            
        Returns:
            Complete evaluation and debrief report
        """
        logger.info(f"Completing scenario {session_id}: {reason}")
        
        # Retrieve session
        session = self.active_sessions.get(session_id)
        if not session:
            session = await self.session_manager.load_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
        
        # Mark session as complete
        session.end_time = datetime.now().timestamp()
        session.current_state = "completed"
        session.is_active = False
        
        # Request evaluation from Evaluation Agent
        evaluation_message = AgentMessage(
            sender_agent="orchestrator",
            recipient_agent="evaluation_agent",
            message_type="evaluate_session",
            session_id=session_id,
            payload={
                "session": session.model_dump(),
                "completion_reason": reason
            }
        )
        
        evaluation_response = await self.evaluation_agent.process_message(evaluation_message)
        evaluation_data = evaluation_response.payload.get("evaluation", {})
        
        # Update user profile with evaluation results
        await self._update_user_profile(session, evaluation_data)
        
        # Generate debrief
        debrief = await self._generate_debrief(session, evaluation_data)
        
        # Save final session state
        await self.session_manager.save_session(session)
        
        # Remove from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        logger.success(f"✅ Scenario {session_id} completed successfully")
        
        return {
            "session_id": session_id,
            "evaluation": evaluation_data,
            "debrief": debrief,
            "duration_seconds": session.calculate_session_duration(),
            "completion_reason": reason
        }
    
    async def _notify_evaluation_agent(
        self,
        event_type: str,
        session: CyberGuardSession,
        decision_point: Optional[DecisionPoint] = None
    ) -> None:
        """Send notification to evaluation agent for invisible assessment."""
        message = AgentMessage(
            sender_agent="orchestrator",
            recipient_agent="evaluation_agent",
            message_type=event_type,
            session_id=session.session_id,
            payload={
                "session_id": session.session_id,
                "user_id": session.user_id,
                "scenario_type": session.scenario_type.value,
                "decision_point": decision_point.model_dump() if decision_point else None
            }
        )
        
        await self.evaluation_agent.process_message(message)
    
    async def _update_user_profile(
        self,
        session: CyberGuardSession,
        evaluation_data: Dict[str, Any]
    ) -> None:
        """Update user profile based on session evaluation."""
        message = AgentMessage(
            sender_agent="orchestrator",
            recipient_agent="memory_manager",
            message_type="update_profile",
            session_id=session.session_id,
            payload={
                "user_id": session.user_id,
                "session_id": session.session_id,
                "evaluation": evaluation_data,
                "session_data": session.model_dump()
            }
        )
        
        await self.memory_manager.process_message(message)
    
    async def _generate_debrief(
        self,
        session: CyberGuardSession,
        evaluation_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate learning debrief using Game Master's debrief tool."""
        if not evaluation_data:
            # Request evaluation if not provided
            eval_message = AgentMessage(
                sender_agent="orchestrator",
                recipient_agent="evaluation_agent",
                message_type="get_evaluation",
                session_id=session.session_id,
                payload={"session_id": session.session_id}
            )
            eval_response = await self.evaluation_agent.process_message(eval_message)
            evaluation_data = eval_response.payload.get("evaluation", {})
        
        # Generate debrief
        debrief = await self.game_master.debrief_generator.generate_debrief(
            session=session,
            completion_reason="normal_completion"
        )
        
        
        debrief["evaluation"] = evaluation_data
        
        return debrief


# Module-level orchestrator instance
_orchestrator: Optional[CyberGuardOrchestrator] = None


async def get_orchestrator() -> CyberGuardOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    
    if _orchestrator is None:
        _orchestrator = CyberGuardOrchestrator()
        await _orchestrator.initialize()
    
    return _orchestrator


async def main():
    """Main entry point for standalone execution."""
    logger.info("🎯 Starting CyberGuard Academy")
    
    try:
        # Initialize orchestrator
        orchestrator = CyberGuardOrchestrator()
        await orchestrator.initialize()
        
        # Example: Run a simple scenario
        logger.info("Running example phishing scenario...")
        
        # Create session
        session = await orchestrator.create_session(
            user_id="demo_user_001",
            threat_type="phishing",
            difficulty=3,
            user_role="developer"
        )
        
        logger.info(f"Session created: {session.session_id}")
        logger.info(f"Opening narrative: {session.conversation_history[0]['content']}")
        
        # Simulate user interaction
        response1 = await orchestrator.process_user_action(
            session_id=session.session_id,
            user_message="I received an email about my account being suspended",
            action_type="message"
        )
        
        logger.info(f"Game Master response: {response1['narrative']}")
        
        # Complete scenario
        result = await orchestrator.complete_scenario(session.session_id)
        
        logger.info("📊 Scenario Results:")
        logger.info(f"Duration: {result['duration_seconds']:.1f} seconds")
        logger.info(f"Score: {result['evaluation'].get('overall_score', 0):.1f}/100")
        logger.info(f"Risk Level: {result['evaluation'].get('risk_level', 'unknown')}")
        
        # Shutdown
        await orchestrator.shutdown()
        
        logger.success("✅ CyberGuard Academy demo completed successfully")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise
    finally:
        if _orchestrator:
            await _orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
