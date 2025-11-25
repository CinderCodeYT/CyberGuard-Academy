"""
Core data models for CyberGuard Academy multi-agent system.

This module defines the essential data structures used throughout the system
for session management, agent communication, and evaluation tracking.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
import uuid
import time


class ThreatType(str, Enum):
    """Types of cybersecurity threats that can be simulated."""
    PHISHING = "phishing"
    VISHING = "vishing"
    BEC = "bec"  # Business Email Compromise
    PHYSICAL = "physical"
    INSIDER = "insider"


class SocialEngineeringPattern(str, Enum):
    """Common social engineering patterns used in scenarios."""
    URGENCY = "urgency"
    AUTHORITY = "authority"
    CURIOSITY = "curiosity"
    FEAR = "fear"
    GREED = "greed"


class DifficultyLevel(int, Enum):
    """Difficulty levels for adaptive training scenarios."""
    BEGINNER = 1
    NOVICE = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


class UserRole(str, Enum):
    """User job roles for personalized scenario generation."""
    DEVELOPER = "developer"
    MANAGER = "manager"
    EXECUTIVE = "executive"
    HR = "hr"
    FINANCE = "finance"
    IT_ADMIN = "it_admin"
    GENERAL = "general"


class DecisionPoint(BaseModel):
    """
    Records a key decision point made by the user during a scenario.
    Used for invisible assessment and learning analytics.
    """
    turn: int = Field(..., description="Conversation turn number when decision was made")
    vulnerability: str = Field(..., description="Type of vulnerability being tested")
    user_choice: str = Field(..., description="What the user chose to do")
    correct_choice: str = Field(..., description="What the optimal security action would be")
    risk_score_impact: float = Field(..., description="Impact on overall risk score (-1.0 to 1.0)")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp of decision")
    confidence_level: Optional[float] = Field(None, description="User's confidence in their choice (0.0-1.0)")


class AgentMessage(BaseModel):
    """
    Standardized message format for Agent-to-Agent (A2A) communication.
    Used by Game Master to coordinate with specialized threat actors.
    """
    sender_agent: str = Field(..., description="Name of the sending agent")
    recipient_agent: str = Field(..., description="Name of the receiving agent")
    message_type: str = Field(..., description="Type of message (activate_scenario, scenario_ready, etc.)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message content and context")
    session_id: str = Field(..., description="ID of the current training session")
    timestamp: float = Field(default_factory=time.time, description="Unix timestamp when message was created")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="For tracking request/response pairs")


class ScenarioContext(BaseModel):
    """
    Context information passed to threat actor agents for scenario generation.
    Contains user profile and session state for personalization.
    """
    user_role: UserRole = Field(..., description="User's job function for scenario personalization")
    difficulty_level: DifficultyLevel = Field(..., description="Current difficulty setting")
    threat_pattern: SocialEngineeringPattern = Field(..., description="Primary social engineering pattern to use")
    recently_seen_patterns: List[str] = Field(default_factory=list, description="Patterns used in recent scenarios to avoid repetition")
    vulnerability_areas: List[str] = Field(default_factory=list, description="Known user weaknesses to focus on")
    session_context: Optional[str] = Field(None, description="Current narrative context from Game Master")


class CyberGuardSession(BaseModel):
    """
    Main session object tracking state across a complete training scenario.
    Manages conversation history, decision tracking, and agent coordination.
    """
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique session identifier")
    user_id: str = Field(..., description="Anonymized user identifier")
    scenario_type: ThreatType = Field(..., description="Type of threat being simulated")
    scenario_id: str = Field(..., description="Specific scenario being run")
    
    # Session state
    current_state: str = Field(default="intro", description="Current stage of scenario progression")
    current_phase: str = Field(default="intro", description="Current phase of the scenario")
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, description="Complete dialogue history")
    decision_points: List[DecisionPoint] = Field(default_factory=list, description="Key user decisions for evaluation")
    threat_actor_active: Optional[str] = Field(None, description="Which threat agent is currently engaged")
    
    # Timing and engagement
    start_time: float = Field(default_factory=time.time, description="When scenario started")
    end_time: Optional[float] = Field(None, description="When scenario completed")
    hints_used: int = Field(default=0, description="Number of hints provided to user")
    pause_count: int = Field(default=0, description="Times user paused/resumed scenario")
    is_active: bool = Field(default=True, description="Whether session is currently active")
    
    # User context
    user_role: UserRole = Field(..., description="User's job function")
    current_difficulty: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE, description="Adaptive difficulty level")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Session creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")

    def add_message(self, role: str, content: str) -> None:
        """Add a conversation message and update timestamp."""
        self.conversation_history.append({"role": role, "content": content})
        self.updated_at = datetime.now(timezone.utc)

    def record_decision(self, decision: DecisionPoint) -> None:
        """Record a user decision point for evaluation."""
        self.decision_points.append(decision)
        self.updated_at = datetime.now(timezone.utc)

    def calculate_session_duration(self) -> float:
        """Calculate total session duration in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time

    def get_recent_patterns(self, limit: int = 5) -> List[str]:
        """Get recently used patterns to avoid repetition."""
        # This would typically query user's session history
        # For now, return empty list - will be implemented with Memory Manager
        return []


class UserProfile(BaseModel):
    """
    Long-term user profile stored by Memory Manager.
    Tracks learning progress and vulnerability patterns across sessions.
    """
    user_id: str = Field(..., description="Anonymized user identifier")
    role: UserRole = Field(..., description="User's primary job function")
    
    # Learning progress
    total_sessions: int = Field(default=0, description="Total training sessions completed")
    average_score: float = Field(default=0.0, description="Average performance score across sessions")
    current_difficulty: DifficultyLevel = Field(default=DifficultyLevel.INTERMEDIATE, description="Current adaptive difficulty")
    
    # Vulnerability tracking
    vulnerability_patterns: Dict[str, float] = Field(default_factory=dict, description="Weakness scores by pattern type")
    improvement_trends: Dict[str, List[float]] = Field(default_factory=dict, description="Score trends over time by category")
    last_seen_scenarios: List[str] = Field(default_factory=list, description="Recently completed scenario IDs")
    
    # Engagement metrics
    average_session_time: float = Field(default=0.0, description="Average time spent per session")
    hint_usage_rate: float = Field(default=0.0, description="Percentage of scenarios where hints were used")
    completion_rate: float = Field(default=0.0, description="Percentage of scenarios completed vs abandoned")
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Profile creation date")
    last_session_at: Optional[datetime] = Field(None, description="Most recent session timestamp")
    
    def update_from_session(self, session: CyberGuardSession) -> None:
        """Update profile based on completed session results."""
        self.total_sessions += 1
        self.last_session_at = datetime.now(timezone.utc)
        # Additional update logic would be implemented here
        

class EvaluationResult(BaseModel):
    """
    Results from evaluating a completed training session.
    Used by Evaluation Agent to assess learning effectiveness.
    """
    session_id: str = Field(..., description="ID of evaluated session")
    user_id: str = Field(..., description="Anonymized user identifier")
    
    # Overall scores
    overall_risk_score: float = Field(..., description="Calculated risk score (0.0-1.0, lower is better)")
    threat_recognition_score: float = Field(..., description="How well user identified threats (0.0-1.0)")
    response_quality_score: float = Field(..., description="Quality of user's security actions (0.0-1.0)")
    
    # Detailed breakdown
    decisions_analyzed: int = Field(..., description="Total decision points evaluated")
    correct_decisions: int = Field(..., description="Number of optimal security choices made")
    missed_red_flags: List[str] = Field(default_factory=list, description="Security indicators user missed")
    knowledge_gaps: List[str] = Field(default_factory=list, description="Areas needing additional training")
    
    # Performance metrics
    average_response_time: float = Field(..., description="Average time to make security decisions")
    confidence_correlation: Optional[float] = Field(None, description="Correlation between confidence and correctness")
    
    # Recommendations
    suggested_difficulty: DifficultyLevel = Field(..., description="Recommended difficulty for next session")
    focus_areas: List[str] = Field(default_factory=list, description="Vulnerability patterns to emphasize")
    
    # Metadata
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="When evaluation was performed")
    evaluator_version: str = Field(default="1.0", description="Version of evaluation algorithm used")