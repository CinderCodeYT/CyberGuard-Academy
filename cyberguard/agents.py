"""
Base classes and interfaces for CyberGuard Academy agents.

Defines the core agent interfaces and common functionality that all
specialized agents (Game Master, Threat Actors, Evaluation) will inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from cyberguard.models import AgentMessage, ScenarioContext, CyberGuardSession


class BaseAgent(ABC):
    """
    Base class for all CyberGuard Academy agents.
    
    Provides common functionality and defines the interface that all
    agents must implement for consistent A2A communication.
    """
    
    def __init__(self, agent_name: str, agent_type: str):
        """
        Initialize base agent.
        
        Args:
            agent_name: Unique identifier for this agent instance
            agent_type: Category of agent (orchestrator, threat_actor, evaluator, memory)
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.active_sessions: Dict[str, CyberGuardSession] = {}
        
    @abstractmethod
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """
        Process incoming A2A message from another agent.
        
        Args:
            message: Incoming message following A2A protocol
            
        Returns:
            Response message to send back to sender
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize agent resources and connections."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up agent resources and active sessions."""
        pass
    
    def create_response_message(
        self, 
        original_message: AgentMessage, 
        message_type: str, 
        payload: Dict[str, Any]
    ) -> AgentMessage:
        """
        Create standardized response message.
        
        Args:
            original_message: Message being responded to
            message_type: Type of response message
            payload: Response content
            
        Returns:
            Formatted response message
        """
        return AgentMessage(
            sender_agent=self.agent_name,
            recipient_agent=original_message.sender_agent,
            message_type=message_type,
            payload=payload,
            session_id=original_message.session_id,
            correlation_id=original_message.correlation_id
        )


class OrchestratorAgent(BaseAgent):
    """
    Base class for orchestrator agents (Game Master).
    
    Handles scenario flow, agent coordination, and narrative management.
    """
    
    def __init__(self, agent_name: str = "game_master"):
        super().__init__(agent_name, "orchestrator")
    
    @abstractmethod
    async def start_scenario(
        self, 
        user_id: str, 
        scenario_type: str, 
        context: ScenarioContext
    ) -> CyberGuardSession:
        """
        Start a new training scenario.
        
        Args:
            user_id: Anonymized user identifier
            scenario_type: Type of threat to simulate
            context: User context and preferences
            
        Returns:
            New session object
        """
        pass
    
    @abstractmethod
    async def coordinate_with_agent(
        self, 
        target_agent: str, 
        action: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send coordination message to specialized agent.
        
        Args:
            target_agent: Name of agent to coordinate with
            action: Action to request from agent
            context: Context data for the action
            
        Returns:
            Response from target agent
        """
        pass


class ThreatActorAgent(BaseAgent):
    """
    Base class for threat actor agents (Phishing, Vishing, etc.).
    
    Generates realistic threat scenarios based on social engineering patterns.
    """
    
    def __init__(self, agent_name: str, threat_type: str):
        super().__init__(agent_name, "threat_actor")
        self.threat_type = threat_type
    
    @abstractmethod
    async def generate_scenario(self, context: ScenarioContext) -> Dict[str, Any]:
        """
        Generate a threat scenario based on context.
        
        Args:
            context: Scenario generation parameters
            
        Returns:
            Generated scenario content and metadata
        """
        pass
    
    @abstractmethod
    async def adapt_scenario(
        self, 
        session_id: str, 
        user_response: str, 
        performance_hint: str
    ) -> Dict[str, Any]:
        """
        Adapt ongoing scenario based on user responses.
        
        Args:
            session_id: Current session identifier
            user_response: Latest user input
            performance_hint: Guidance on difficulty adjustment
            
        Returns:
            Adapted scenario content
        """
        pass


class EvaluationAgent(BaseAgent):
    """
    Base class for evaluation agents.
    
    Provides invisible assessment and learning analytics.
    """
    
    def __init__(self, agent_name: str = "evaluation_agent"):
        super().__init__(agent_name, "evaluator")
    
    @abstractmethod
    async def track_decision(
        self, 
        session_id: str, 
        decision_data: Dict[str, Any]
    ) -> None:
        """
        Track a user decision point for evaluation.
        
        Args:
            session_id: Session where decision was made
            decision_data: Decision details and context
        """
        pass
    
    @abstractmethod
    async def calculate_session_score(self, session: CyberGuardSession) -> Dict[str, Any]:
        """
        Calculate comprehensive evaluation for completed session.
        
        Args:
            session: Completed training session
            
        Returns:
            Evaluation results and recommendations
        """
        pass


class MemoryAgent(BaseAgent):
    """
    Base class for memory management agents.
    
    Handles persistent storage and retrieval of user progress and session data.
    """
    
    def __init__(self, agent_name: str = "memory_agent"):
        super().__init__(agent_name, "memory")
    
    @abstractmethod
    async def store_session(self, session: CyberGuardSession) -> None:
        """
        Store completed session data.
        
        Args:
            session: Session to store
        """
        pass
    
    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user profile and learning history.
        
        Args:
            user_id: User to look up
            
        Returns:
            User profile data if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update_user_patterns(
        self, 
        user_id: str, 
        vulnerability_data: Dict[str, Any]
    ) -> None:
        """
        Update user's vulnerability patterns based on session results.
        
        Args:
            user_id: User to update
            vulnerability_data: New vulnerability insights
        """
        pass