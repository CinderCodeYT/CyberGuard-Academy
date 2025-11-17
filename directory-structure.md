# Directory Structure, Core Classes and Tools

## Directory Structure

```bash
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
``` 


## Core Data Models (`cyberguard/models.py`)

- **CyberGuardSession:** Complete session management with conversation history and decision tracking
    - `add_message`: Add a new message to conversation history  
    - `record_decision`: Record a user decision for evaluation
    - `calculate_session_duration`: Calculate total session duration in seconds
    - `get_recent_patterns`: Get recently used patterns to avoid repetition  
- **DecisionPoint:** Invisible assessment tracking for learning analytics
- **AgentMessage:** Standardized A2A protocol communication
- **ScenarioContext:** User-personalized threat generation context
- **UserProfile:** Long-term learning progress and vulnerability patterns
- **EvaluationResult:** Comprehensive session assessment and recommendations
- **Enums:** ThreatType, SocialEngineeringPattern, DifficultyLevel, UserRole


## Configuration System (`cyberguard/config.py`)

Environment-specific settings with validation  
- Default environment: `development`  

Model configuration (Gemini Pro/Flash)  
- Default pro model: `gemini-2.5-pro`  
- Default flash model: `gemini-25.-flash`  

Agent configuration  
- Default turns: 15  
- Default difficulty: 3

Security settings with safe redirect handling  
Observability configuration for Cloud Trace/Logging  
Development vs. production switches  
- `is_development`: Checks if running in development environment
- `is_production`: Checks if running in production environment


## Agent Architecture (`cyberguard/agents.py`)

- **BaseAgent:** Common A2A protocol interface
    - `process_message`: Process incoming A2A message from another agent
    - `initialize`: Initiliaze agent resources and active sessions
    - `shutdown`: Clean up agent resources and active sessions
    - `create_response_message`: Create standardized response message
- **OrchestratorAgent:** Game Master base class
    - `start_scenario`: Start a new training scenario
    - `coordinate_with_agent`: Send a coordination message to a specialized agent
- **ThreatActorAgent:** Specialized threat simulation base
    - `generate_scenario`: Generates a threate scenario based on context
    - `adapt_scenario`: Adapt the ongoing scenario on user responses
- **EvaluationAgent:** Invisible assessment base
    - `track_decision`: Track a user decision point for evaluation
    - `calculate_session_score`: Calculate a comprehensive evaluation for completed session
- **MemoryAgent:** Persistent storage base
    - `store_session`: Stores completed session data
    - `get_user_profile`: Retrieve user profile and learning history
    - `update_user_patterns`: Update user's vulnerability patterns based on session results


## Test Framework (`tests/`)

- **test_models.py:** Comprehensive model validation tests
- **test_integration.py:** Agent coordination and performance tests
- **conftest.py:** Shared fixtures and test configuration
- Markers for unit, integration, agent-specific, and evaluation tests

