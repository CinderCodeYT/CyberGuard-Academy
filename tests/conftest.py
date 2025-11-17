"""Test configuration and shared fixtures for CyberGuard Academy tests."""

import pytest
import asyncio
from unittest.mock import Mock
from typing import Generator

# Test data and fixtures for reuse across test modules


@pytest.fixture
def sample_user_id() -> str:
    """Provide a sample anonymized user ID for testing."""
    return "test_user_12345"


@pytest.fixture 
def sample_session_data() -> dict:
    """Provide sample session data for testing."""
    return {
        "user_id": "test_user_12345",
        "scenario_type": "phishing",
        "scenario_id": "phish_basic_001",
        "user_role": "developer"
    }


@pytest.fixture
def mock_game_master() -> Mock:
    """Provide a mock Game Master agent for testing."""
    game_master = Mock()
    game_master.coordinate_with_agent = Mock()
    game_master.generate_scenario = Mock()
    game_master.process_user_response = Mock()
    return game_master


@pytest.fixture
def mock_phishing_agent() -> Mock:
    """Provide a mock Phishing Agent for testing."""
    phishing_agent = Mock()
    phishing_agent.generate_email = Mock(return_value={
        "subject": "URGENT: Account Verification Required",
        "sender": "security@yourbankname.com", 
        "body": "Your account will be suspended...",
        "red_flags": ["urgency", "suspicious_domain", "generic_greeting"]
    })
    return phishing_agent


@pytest.fixture
def mock_evaluation_agent() -> Mock:
    """Provide a mock Evaluation Agent for testing."""
    evaluation_agent = Mock()
    evaluation_agent.track_decision = Mock()
    evaluation_agent.calculate_risk_score = Mock(return_value=0.65)
    evaluation_agent.generate_feedback = Mock()
    return evaluation_agent


@pytest.fixture
def sample_decision_points() -> list:
    """Provide sample decision point data for testing."""
    return [
        {
            "turn": 1,
            "vulnerability": "suspicious_sender",
            "user_choice": "clicked_link",
            "correct_choice": "verify_sender",
            "risk_score_impact": 0.8
        },
        {
            "turn": 3, 
            "vulnerability": "urgency_pressure",
            "user_choice": "ignored_pressure",
            "correct_choice": "ignored_pressure",
            "risk_score_impact": -0.2
        }
    ]


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test constants
TEST_SCENARIOS = {
    "phishing_basic": {
        "id": "phish_basic_001",
        "difficulty": 2,
        "pattern": "urgency",
        "expected_duration": 300  # 5 minutes
    },
    "phishing_advanced": {
        "id": "phish_adv_001", 
        "difficulty": 4,
        "pattern": "authority",
        "expected_duration": 450  # 7.5 minutes
    }
}

PERFORMANCE_TARGETS = {
    "engagement_rate": 0.8,      # 80%+ completion
    "improvement_rate": 0.4,     # 40%+ learning improvement
    "response_time": 2.0,        # <2s agent response
    "error_rate": 0.005,         # <0.5% error rate
    "success_rate": 0.7          # 70% target for adaptive difficulty
}