"""
Game Master Agent - Central orchestrator for CyberGuard Academy training scenarios.

The Game Master is responsible for:
1. Managing scenario flow and narrative progression
2. Coordinating with specialized threat actor agents
3. Maintaining conversational immersion during training
4. Providing adaptive hints and guidance when needed
5. Triggering evaluation and debrief processes

This serves as the reference implementation for all other agents in the system.
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from cyberguard.agents import OrchestratorAgent
from cyberguard.models import (
    AgentMessage, 
    CyberGuardSession, 
    ScenarioContext, 
    DecisionPoint,
    ThreatType,
    SocialEngineeringPattern,
    DifficultyLevel,
    UserRole
)
from cyberguard.config import settings
from cyberguard.gemini_client import GeminiClient
from tools.scenario_selector import ScenarioSelector
from tools.agent_coordinator import AgentCoordinator
from tools.narrative_manager import NarrativeManager
from tools.hint_provider import HintProvider
from tools.debrief_generator import DebriefGenerator


class GameMasterAgent(OrchestratorAgent):
    """
    Game Master Agent - Central orchestrator for training scenarios.
    
    This agent manages the complete lifecycle of a cybersecurity training scenario:
    - Selects appropriate scenarios based on user profile
    - Coordinates with threat actor agents to generate realistic threats
    - Maintains conversational flow and narrative immersion
    - Provides adaptive hints when users struggle
    - Triggers evaluation and generates learning debriefs
    
    Key Design Principles:
    1. Never break immersion during active scenarios
    2. Coordinate seamlessly with specialized agents via A2A protocol
    3. Adapt difficulty based on user performance (target 70% success rate)
    4. Provide learning moments naturally after decisions
    """
    
    def __init__(self):
        super().__init__("game_master")
        
        # Initialize tools
        self.scenario_selector = ScenarioSelector()
        self.agent_coordinator = AgentCoordinator()
        self.narrative_manager = NarrativeManager()
        self.hint_provider = HintProvider()
        self.debrief_generator = DebriefGenerator()
        
        # Agent state
        self.available_threat_agents = [
            "phishing_agent",
            "vishing_agent", 
            "bec_agent",
            "physical_agent",
            "insider_agent"
        ]
        # active_coordinations is now inherited from OrchestratorAgent
        
    async def initialize(self) -> None:
        """Initialize Game Master and verify threat agent availability."""
        print(f"[{self.agent_name}] Initializing Game Master Agent...")
        
        # Initialize all tools
        await self.scenario_selector.initialize()
        await self.agent_coordinator.initialize()
        await self.narrative_manager.initialize()
        await self.hint_provider.initialize()
        await self.debrief_generator.initialize()
        
        # Verify threat agents are available (in production, this would check actual agent endpoints)
        if settings.is_development:
            print(f"[{self.agent_name}] Development mode: Using mock threat agents")
        else:
            # In production, ping each threat agent to verify availability
            available_agents = await self.agent_coordinator.check_agent_availability(
                self.available_threat_agents
            )
            self.available_threat_agents = available_agents
            print(f"[{self.agent_name}] Available threat agents: {available_agents}")
        
        print(f"[{self.agent_name}] Game Master initialized successfully")

    async def shutdown(self) -> None:
        """Gracefully shutdown Game Master and complete active sessions."""
        print(f"[{self.agent_name}] Shutting down Game Master...")
        
        # Complete any active sessions
        for session_id, session in self.active_sessions.items():
            if session.end_time is None:
                print(f"[{self.agent_name}] Completing active session: {session_id}")
                await self.complete_scenario(session_id, reason="system_shutdown")
        
        # Shutdown tools
        await self.scenario_selector.shutdown()
        await self.agent_coordinator.shutdown()
        await self.narrative_manager.shutdown()
        await self.hint_provider.shutdown()
        await self.debrief_generator.shutdown()
        
        print(f"[{self.agent_name}] Game Master shutdown complete")

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """
        Process incoming A2A messages from other agents.
        
        Handles coordination responses, evaluation updates, and memory notifications.
        """
        try:
            print(f"[{self.agent_name}] Processing message: {message.message_type} from {message.sender_agent}")
            
            if message.message_type == "scenario_ready":
                return await self._handle_scenario_ready(message)
            elif message.message_type == "evaluation_complete":
                return await self._handle_evaluation_complete(message)
            elif message.message_type == "memory_updated":
                return await self._handle_memory_updated(message)
            elif message.message_type == "agent_error":
                return await self._handle_agent_error(message)
            else:
                return self.create_response_message(
                    message,
                    "error",
                    {"error": f"Unknown message type: {message.message_type}"}
                )
                
        except Exception as e:
            print(f"[{self.agent_name}] Error processing message: {str(e)}")
            return self.create_response_message(
                message,
                "error", 
                {"error": f"Failed to process message: {str(e)}"}
            )

    async def start_scenario(
        self, 
        user_id: str, 
        scenario_type: str, 
        context: ScenarioContext
    ) -> CyberGuardSession:
        """
        Start a new cybersecurity training scenario.
        
        This is the main entry point for beginning training sessions.
        """
        print(f"[{self.agent_name}] Starting scenario for user {user_id}: {scenario_type}")
        
        # Create new session
        session = CyberGuardSession(
            user_id=user_id,
            scenario_type=ThreatType(scenario_type),
            scenario_id=f"{scenario_type}_{uuid.uuid4().hex[:8]}",
            user_role=context.user_role,
            current_difficulty=context.difficulty_level
        )
        
        # Store session
        self.active_sessions[session.session_id] = session
        
        # Select specific scenario based on context
        scenario_details = await self.scenario_selector.select_scenario(
            user_role=context.user_role,
            difficulty_level=context.difficulty_level,
            threat_type=scenario_type,
            recently_seen_patterns=context.recently_seen_patterns,
            vulnerability_areas=context.vulnerability_areas
        )
        
        # Generate opening narrative
        opening_narrative = await self.narrative_manager.generate_opening(
            scenario_details=scenario_details,
            user_context=context
        )
        
        # Add opening to conversation
        session.add_message("game_master", opening_narrative)
        session.current_state = "scenario_intro"
        
        print(f"[{self.agent_name}] Scenario {session.session_id} started successfully")
        return session

    async def coordinate_with_agent(
        self, 
        target_agent: str, 
        action: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate with specialized threat actor agents via A2A protocol.
        
        This uses the base class coordination pattern and adds Game Master
        specific coordination logic through the agent coordinator tool.
        """
        session_id = context.get("session_id", "")
        
        print(f"[{self.agent_name}] Coordinating with {target_agent}: {action}")
        
        # Use base class method to create and track the message
        message = await self.send_coordination_message(
            target_agent=target_agent,
            message_type=action,
            payload=context,
            session_id=session_id
        )
        
        # Send message via agent coordinator tool and get response
        response = await self.agent_coordinator.send_message(target_agent, message)
        
        # Update coordination state
        if message.correlation_id in self.active_coordinations:
            self.active_coordinations[message.correlation_id].update({
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "response": response
            })
        
        return response

    async def handle_user_response(
        self, 
        session_id: str, 
        user_input: str
    ) -> Dict[str, Any]:
        """
        Handle user input during an active scenario.
        
        This method orchestrates the complete flow of user interaction.
        """
        if session_id not in self.active_sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.active_sessions[session_id]
        print(f"[{self.agent_name}] Handling user response in session {session_id}")
        
        # Add user input to conversation
        session.add_message("user", user_input)
        
        # Analyze user response for decision points
        decision_analysis = await self.narrative_manager.analyze_user_response(
            user_input=user_input,
            session_context=session,
            current_scenario_state=session.current_state
        )
        
        # If this represents a decision point, record it
        if decision_analysis.get("is_decision_point", False):
            decision = DecisionPoint(
                turn=len(session.conversation_history),
                vulnerability=decision_analysis["vulnerability_type"],
                user_choice=decision_analysis["user_action"],
                correct_choice=decision_analysis["optimal_action"],
                risk_score_impact=decision_analysis["risk_impact"],
                confidence_level=decision_analysis.get("user_confidence")
            )
            session.record_decision(decision)
            
            # Notify evaluation agent of decision (A2A coordination)
            await self.coordinate_with_agent(
                target_agent="evaluation_agent",
                action="track_decision",
                context={
                    "session_id": session_id,
                    "decision": decision.model_dump(),
                    "user_profile": {"role": session.user_role.value}
                }
            )
        
        # Determine next response based on current state and user action
        if session.current_state == "scenario_intro":
            response = await self._handle_intro_response(session, user_input, decision_analysis)
        elif session.current_state == "scenario_active":
            response = await self._handle_active_scenario_response(session, user_input, decision_analysis)
        elif session.current_state == "awaiting_decision":
            response = await self._handle_decision_response(session, user_input, decision_analysis)
        else:
            response = await self._handle_general_response(session, user_input)
        
        # Add Game Master response to conversation
        session.add_message("game_master", response["content"])
        
        # Check if scenario should end
        if (len(session.conversation_history) >= settings.max_conversation_turns or 
            response.get("scenario_complete", False)):
            await self.complete_scenario(session_id)
            response["scenario_complete"] = True
        
        return response

    async def _handle_intro_response(
        self, 
        session: CyberGuardSession, 
        user_input: str, 
        decision_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user response during scenario introduction."""
        
        # Activate appropriate threat actor based on scenario type
        threat_agent = f"{session.scenario_type.value}_agent"
        
        if threat_agent in self.available_threat_agents:
            # Request threat scenario from specialized agent
            threat_response = await self.coordinate_with_agent(
                target_agent=threat_agent,
                action="generate_scenario",
                context={
                    "session_id": session.session_id,
                    "user_role": session.user_role.value,
                    "difficulty": session.current_difficulty.value,
                    "user_context": user_input
                }
            )
            
            # Generate narrative that incorporates the threat
            narrative = await self.narrative_manager.generate_threat_presentation(
                threat_content=threat_response.get("scenario_content", {}),
                user_context=user_input,
                session=session
            )
            
            session.current_state = "scenario_active"
            session.threat_actor_active = threat_agent
            
        else:
            # Fallback to built-in scenario if threat agent unavailable
            narrative = await self.narrative_manager.generate_fallback_scenario(
                scenario_type=session.scenario_type,
                user_context=user_input
            )
            session.current_state = "scenario_active"
        
        return {
            "content": narrative,
            "session_state": session.current_state,
            "requires_decision": True
        }

    async def _handle_active_scenario_response(
        self, 
        session: CyberGuardSession, 
        user_input: str, 
        decision_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user response during active threat scenario."""
        
        # Check if user needs a hint
        if decision_analysis.get("user_struggling", False) and session.hints_used < 3:
            hint = await self.hint_provider.generate_hint(
                user_input=user_input,
                session_context=session,
                decision_analysis=decision_analysis
            )
            if hint:
                session.hints_used += 1
                response_content = f"{hint}\n\n"
            else:
                response_content = ""
        else:
            response_content = ""
        
        # Generate adaptive narrative based on user choice
        narrative = await self.narrative_manager.generate_adaptive_response(
            user_action=decision_analysis.get("user_action", "unclear"),
            session_context=session,
            decision_quality=decision_analysis.get("decision_quality", "neutral")
        )
        
        response_content += narrative
        
        # Update session state based on user action
        if decision_analysis.get("scenario_resolved", False):
            session.current_state = "scenario_complete"
            return {
                "content": response_content,
                "session_state": session.current_state,
                "scenario_complete": True
            }
        else:
            session.current_state = "awaiting_decision"
            return {
                "content": response_content,
                "session_state": session.current_state,
                "requires_decision": True
            }

    async def _handle_decision_response(
        self, 
        session: CyberGuardSession, 
        user_input: str, 
        decision_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle user response when a decision is required."""
        
        # If user made a clear security decision
        if decision_analysis.get("is_security_decision", False):
            
            # Generate learning moment based on decision quality
            learning_content = await self.narrative_manager.generate_learning_moment(
                user_decision=decision_analysis["user_action"],
                optimal_action=decision_analysis["optimal_action"],
                vulnerability_type=decision_analysis["vulnerability_type"],
                session_context=session
            )
            
            session.current_state = "scenario_complete"
            return {
                "content": learning_content,
                "session_state": session.current_state,
                "scenario_complete": True
            }
        
        # If user needs clarification or is exploring
        else:
            narrative = await self.narrative_manager.generate_clarification(
                user_input=user_input,
                session_context=session
            )
            
            return {
                "content": narrative,
                "session_state": session.current_state,
                "requires_decision": True
            }

    async def _handle_general_response(
        self, 
        session: CyberGuardSession, 
        user_input: str
    ) -> Dict[str, Any]:
        """Handle general user responses that don't fit other categories."""
        
        narrative = await self.narrative_manager.generate_general_response(
            user_input=user_input,
            session_context=session
        )
        
        return {
            "content": narrative,
            "session_state": session.current_state,
            "requires_decision": False
        }

    async def complete_scenario(self, session_id: str, reason: str = "natural_completion") -> Dict[str, Any]:
        """Complete a training scenario and generate debrief."""
        
        if session_id not in self.active_sessions:
            return {"error": f"Session {session_id} not found"}
        
        session = self.active_sessions[session_id]
        session.end_time = datetime.utcnow().timestamp()
        session.current_state = "completed"
        
        print(f"[{self.agent_name}] Completing scenario {session_id}, reason: {reason}")
        
        # Generate debrief and learning summary
        debrief = await self.debrief_generator.generate_debrief(
            session=session,
            completion_reason=reason
        )
        
        # Add debrief to conversation
        session.add_message("game_master", debrief["content"])
        
        # Trigger final evaluation
        evaluation_response = await self.coordinate_with_agent(
            target_agent="evaluation_agent",
            action="evaluate_session",
            context={
                "session": session.model_dump(),
                "completion_reason": reason
            }
        )
        
        # Store session in memory
        await self.coordinate_with_agent(
            target_agent="memory_agent",
            action="store_session",
            context={
                "session": session.model_dump(),
                "evaluation_results": evaluation_response
            }
        )
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "completion_reason": reason,
            "debrief": debrief,
            "evaluation": evaluation_response,
            "session_duration": session.calculate_session_duration()
        }

    # A2A Message Handlers
    async def _handle_scenario_ready(self, message: AgentMessage) -> AgentMessage:
        """Handle notification that a threat agent has prepared a scenario."""
        
        correlation_id = message.correlation_id
        if correlation_id in self.active_coordinations:
            coordination = self.active_coordinations[correlation_id]
            coordination["status"] = "scenario_ready"
            coordination["scenario_content"] = message.payload
        
        return self.create_response_message(
            message,
            "acknowledged",
            {"status": "scenario_ready_received"}
        )

    async def _handle_evaluation_complete(self, message: AgentMessage) -> AgentMessage:
        """Handle notification that evaluation agent has completed assessment."""
        
        session_id = message.session_id
        if session_id in self.active_sessions:
            # Update session with evaluation insights if needed
            evaluation_data = message.payload
            # Could store evaluation insights for adaptive hints
        
        return self.create_response_message(
            message,
            "acknowledged", 
            {"status": "evaluation_received"}
        )

    async def _handle_memory_updated(self, message: AgentMessage) -> AgentMessage:
        """Handle notification that memory agent has updated user profile."""
        
        return self.create_response_message(
            message,
            "acknowledged",
            {"status": "memory_update_received"}
        )

    async def _handle_agent_error(self, message: AgentMessage) -> AgentMessage:
        """Handle error notifications from other agents."""
        
        error_details = message.payload
        print(f"[{self.agent_name}] Agent error received from {message.sender_agent}: {error_details}")
        
        # Could implement fallback logic here
        
        return self.create_response_message(
            message,
            "error_acknowledged",
            {"status": "error_logged"}
        )

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an active session with Game Master specific details."""
        
        # Get base session status
        status = super().get_session_status(session_id)
        if not status:
            return None
        
        # Add Game Master specific details
        session = self.active_sessions[session_id]
        status.update({
            "decisions_made": len(session.decision_points),
            "hints_used": session.hints_used,
            "threat_actor_active": session.threat_actor_active,
            "duration_seconds": session.calculate_session_duration()
        })
        
        return status

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all currently active sessions with Game Master specific details."""
        
        return [
            self.get_session_status(session_id) 
            for session_id in self.active_sessions.keys()
        ]