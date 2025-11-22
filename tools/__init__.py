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

__all__ = [
    "ScenarioSelector",
    "AgentCoordinator", 
    "NarrativeManager",
    "HintProvider", 
    "DebriefGenerator",
    "EmailGenerator",
    "LinkGenerator",
    "HeaderSpoofing"
]