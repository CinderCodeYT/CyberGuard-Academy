"""Tests for CyberGuard Academy core data models."""

import pytest
from datetime import datetime
from cyberguard.models import (
    CyberGuardSession,
    DecisionPoint,
    AgentMessage,
    ScenarioContext,
    UserProfile,
    EvaluationResult,
    ThreatType,
    SocialEngineeringPattern,
    DifficultyLevel,
    UserRole,
)


class TestCyberGuardSession:
    """Test cases for CyberGuardSession model."""
    
    def test_session_creation(self):
        """Test basic session creation with required fields."""
        session = CyberGuardSession(
            user_id="test_user_123",
            scenario_type=ThreatType.PHISHING,
            scenario_id="phish_001",
            user_role=UserRole.DEVELOPER
        )
        
        assert session.user_id == "test_user_123"
        assert session.scenario_type == ThreatType.PHISHING
        assert session.scenario_id == "phish_001"
        assert session.user_role == UserRole.DEVELOPER
        assert session.current_state == "intro"
        assert session.conversation_history == []
        assert session.decision_points == []
        assert session.hints_used == 0
        assert isinstance(session.session_id, str)
        assert isinstance(session.created_at, datetime)
    
    def test_add_message(self):
        """Test adding messages to conversation history."""
        session = CyberGuardSession(
            user_id="test_user",
            scenario_type=ThreatType.PHISHING,
            scenario_id="test",
            user_role=UserRole.GENERAL
        )
        
        session.add_message("game_master", "Welcome to the scenario!")
        session.add_message("user", "Hello, I'm ready.")
        
        assert len(session.conversation_history) == 2
        assert session.conversation_history[0]["role"] == "game_master"
        assert session.conversation_history[0]["content"] == "Welcome to the scenario!"
        assert session.conversation_history[1]["role"] == "user"
        assert "timestamp" in session.conversation_history[0]
    
    def test_record_decision(self):
        """Test recording user decision points."""
        session = CyberGuardSession(
            user_id="test_user",
            scenario_type=ThreatType.PHISHING,
            scenario_id="test",
            user_role=UserRole.GENERAL
        )
        
        decision = DecisionPoint(
            turn=3,
            vulnerability="suspicious_link",
            user_choice="clicked_link",
            correct_choice="verify_sender",
            risk_score_impact=0.8
        )
        
        session.record_decision(decision)
        
        assert len(session.decision_points) == 1
        assert session.decision_points[0].turn == 3
        assert session.decision_points[0].vulnerability == "suspicious_link"
    
    def test_calculate_session_duration(self):
        """Test session duration calculation."""
        session = CyberGuardSession(
            user_id="test_user",
            scenario_type=ThreatType.PHISHING,
            scenario_id="test",
            user_role=UserRole.GENERAL
        )
        
        # Session should have some duration even without end time
        duration = session.calculate_session_duration()
        assert duration >= 0
        
        # Test with end time
        import time
        session.end_time = time.time() + 300  # 5 minutes later
        duration_with_end = session.calculate_session_duration()
        assert duration_with_end == 300.0


class TestDecisionPoint:
    """Test cases for DecisionPoint model."""
    
    def test_decision_point_creation(self):
        """Test DecisionPoint model validation."""
        decision = DecisionPoint(
            turn=5,
            vulnerability="email_header_spoofing",
            user_choice="trusted_without_verification",
            correct_choice="check_sender_domain",
            risk_score_impact=0.6,
            confidence_level=0.4
        )
        
        assert decision.turn == 5
        assert decision.vulnerability == "email_header_spoofing"
        assert decision.user_choice == "trusted_without_verification"
        assert decision.correct_choice == "check_sender_domain"
        assert decision.risk_score_impact == 0.6
        assert decision.confidence_level == 0.4
        assert isinstance(decision.timestamp, float)


class TestAgentMessage:
    """Test cases for Agent-to-Agent communication."""
    
    def test_agent_message_creation(self):
        """Test AgentMessage model for A2A protocol."""
        message = AgentMessage(
            sender_agent="game_master",
            recipient_agent="phishing_agent",
            message_type="activate_scenario",
            payload={
                "user_role": "developer",
                "difficulty": 3,
                "pattern": "urgency"
            },
            session_id="session_123"
        )
        
        assert message.sender_agent == "game_master"
        assert message.recipient_agent == "phishing_agent"
        assert message.message_type == "activate_scenario"
        assert message.payload["user_role"] == "developer"
        assert message.session_id == "session_123"
        assert isinstance(message.correlation_id, str)
        assert isinstance(message.timestamp, float)


class TestScenarioContext:
    """Test cases for scenario generation context."""
    
    def test_scenario_context_creation(self):
        """Test ScenarioContext model validation."""
        context = ScenarioContext(
            user_role=UserRole.FINANCE,
            difficulty_level=DifficultyLevel.ADVANCED,
            threat_pattern=SocialEngineeringPattern.AUTHORITY,
            recently_seen_patterns=["urgency", "fear"],
            vulnerability_areas=["wire_transfers", "vendor_payments"],
            session_context="User is reviewing quarterly expenses"
        )
        
        assert context.user_role == UserRole.FINANCE
        assert context.difficulty_level == DifficultyLevel.ADVANCED
        assert context.threat_pattern == SocialEngineeringPattern.AUTHORITY
        assert "urgency" in context.recently_seen_patterns
        assert "wire_transfers" in context.vulnerability_areas


class TestUserProfile:
    """Test cases for user profile management."""
    
    def test_user_profile_creation(self):
        """Test UserProfile model with defaults."""
        profile = UserProfile(
            user_id="anonymous_user_456",
            role=UserRole.IT_ADMIN
        )
        
        assert profile.user_id == "anonymous_user_456"
        assert profile.role == UserRole.IT_ADMIN
        assert profile.total_sessions == 0
        assert profile.average_score == 0.0
        assert profile.current_difficulty == DifficultyLevel.INTERMEDIATE
        assert isinstance(profile.vulnerability_patterns, dict)
        assert isinstance(profile.created_at, datetime)
    
    def test_update_from_session(self):
        """Test updating profile from completed session."""
        profile = UserProfile(
            user_id="test_user",
            role=UserRole.DEVELOPER
        )
        
        session = CyberGuardSession(
            user_id="test_user",
            scenario_type=ThreatType.PHISHING,
            scenario_id="test",
            user_role=UserRole.DEVELOPER
        )
        
        original_sessions = profile.total_sessions
        profile.update_from_session(session)
        
        assert profile.total_sessions == original_sessions + 1
        assert profile.last_session_at is not None


class TestEvaluationResult:
    """Test cases for evaluation results."""
    
    def test_evaluation_result_creation(self):
        """Test EvaluationResult model validation."""
        result = EvaluationResult(
            session_id="session_123",
            user_id="user_456",
            overall_risk_score=0.65,
            threat_recognition_score=0.75,
            response_quality_score=0.60,
            decisions_analyzed=8,
            correct_decisions=5,
            missed_red_flags=["suspicious_domain", "urgency_language"],
            knowledge_gaps=["email_header_analysis", "vendor_verification"],
            average_response_time=12.5,
            suggested_difficulty=DifficultyLevel.ADVANCED,
            focus_areas=["authority_tactics", "email_security"]
        )
        
        assert result.session_id == "session_123"
        assert result.overall_risk_score == 0.65
        assert result.decisions_analyzed == 8
        assert result.correct_decisions == 5
        assert "suspicious_domain" in result.missed_red_flags
        assert result.suggested_difficulty == DifficultyLevel.ADVANCED
        assert isinstance(result.evaluated_at, datetime)


class TestEnums:
    """Test cases for enum values."""
    
    def test_threat_types(self):
        """Test ThreatType enum values."""
        assert ThreatType.PHISHING == "phishing"
        assert ThreatType.VISHING == "vishing"
        assert ThreatType.BEC == "bec"
        assert ThreatType.PHYSICAL == "physical"
        assert ThreatType.INSIDER == "insider"
    
    def test_social_engineering_patterns(self):
        """Test SocialEngineeringPattern enum values."""
        assert SocialEngineeringPattern.URGENCY == "urgency"
        assert SocialEngineeringPattern.AUTHORITY == "authority"
        assert SocialEngineeringPattern.CURIOSITY == "curiosity"
        assert SocialEngineeringPattern.FEAR == "fear"
        assert SocialEngineeringPattern.GREED == "greed"
    
    def test_difficulty_levels(self):
        """Test DifficultyLevel enum values."""
        assert DifficultyLevel.BEGINNER == 1
        assert DifficultyLevel.NOVICE == 2
        assert DifficultyLevel.INTERMEDIATE == 3
        assert DifficultyLevel.ADVANCED == 4
        assert DifficultyLevel.EXPERT == 5
    
    def test_user_roles(self):
        """Test UserRole enum values."""
        assert UserRole.DEVELOPER == "developer"
        assert UserRole.MANAGER == "manager"
        assert UserRole.EXECUTIVE == "executive"
        assert UserRole.HR == "hr"
        assert UserRole.FINANCE == "finance"
        assert UserRole.IT_ADMIN == "it_admin"
        assert UserRole.GENERAL == "general"