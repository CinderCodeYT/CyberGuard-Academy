# Directory Structure, Core Classes and Tools

## Directory Structure
agents/  
├── game_master/     # Central orchestrator  
├── phishing/        # Email/message threats    
├── evaluation/      # Assessment logic  
└── memory/          # User progress tracking  
cyberguard/          # Core application  
evaluation/          # Quality assurance framework  
scenarios/           # Threat scenario templates  
terraform/           # Infrastructure as code  
tests/               # Comprehensive test suite  
tools/               # Shared agent tools  


## Core Data Models (`cyberguard/models.py`)

- **CyberGuardSession:** Complete session management with conversation history and decision tracking
- **DecisionPoint:** Invisible assessment tracking for learning analytics
- **AgentMessage:** Standardized A2A protocol communication
- **ScenarioContext:** User-personalized threat generation context
- **UserProfile:** Long-term learning progress and vulnerability patterns
- **EvaluationResult:** Comprehensive session assessment and recommendations
- **Enums:** ThreatType, SocialEngineeringPattern, DifficultyLevel, UserRole


## Configuration System (`cyberguard/config.py`)

Environment-specific settings with validation  
Model configuration (Gemini Pro/Flash)  
Security settings with safe redirect handling  
Observability configuration for Cloud Trace/Logging  
Development vs. production switches  


## Agent Architecture (`cyberguard/agents.py`)

- **BaseAgent:** Common A2A protocol interface
- **OrchestratorAgent:** Game Master base class
- **ThreatActorAgent:** Specialized threat simulation base
- **EvaluationAgent:** Invisible assessment base
- **MemoryAgent:** Persistent storage base


## Test Framework (`tests/`)

- *test_models.py:* Comprehensive model validation tests
- **test_integration.py:** Agent coordination and performance tests
- **conftest.py:** Shared fixtures and test configuration
- Markers for unit, integration, agent-specific, and evaluation tests

