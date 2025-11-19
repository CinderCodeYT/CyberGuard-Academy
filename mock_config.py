"""
Mock configuration for testing without full environment setup.

This allows manual testing of the Game Master without needing
all production dependencies configured.
"""

class MockSettings:
    """Mock settings for testing."""
    
    # Model settings
    gemini_pro_model = "gemini-2.0-flash-exp"
    gemini_flash_model = "gemini-2.0-flash-exp"
    temperature_orchestrator = 0.3
    temperature_threat_actor = 0.7
    
    # Safety settings
    safe_redirect_url = "https://example.com/safe-training-redirect"
    
    # Development settings
    is_development = True
    max_conversation_turns = 20
    
    # Gemini settings (mock)
    google_api_key = "mock-api-key-for-testing"

# Create global settings instance
settings = MockSettings()