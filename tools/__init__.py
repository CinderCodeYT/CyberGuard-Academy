"""Tools package initialization."""

from .scenario_selector import ScenarioSelector
from .agent_coordinator import AgentCoordinator  
from .narrative_manager import NarrativeManager
from .hint_provider import HintProvider
from .debrief_generator import DebriefGenerator

# Threat Actor tools
from .email_generator import EmailGenerator
from .link_generator import LinkGenerator
from .header_spoofing import HeaderSpoofing

# Memory Manager tools
from .session_manager import SessionManager
from .user_profiler import UserProfiler
from .pattern_analyzer import PatternAnalyzer
from .progress_tracker import ProgressTracker

__all__ = [
    "ScenarioSelector",
    "AgentCoordinator", 
    "NarrativeManager",
    "HintProvider", 
    "DebriefGenerator",
    "EmailGenerator",
    "LinkGenerator",
    "HeaderSpoofing",
    "SessionManager",
    "UserProfiler", 
    "PatternAnalyzer",
    "ProgressTracker"
]