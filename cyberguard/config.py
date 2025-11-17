"""
Configuration management for CyberGuard Academy.

Centralized configuration handling with environment variable support,
type validation, and defaults for all system components.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main configuration class for CyberGuard Academy."""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Environment Configuration
    environment: str = Field(default="development", description="Deployment environment")
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Model Configuration
    gemini_pro_model: str = Field(default="gemini-2.5-pro", description="Gemini Pro model identifier")
    gemini_flash_model: str = Field(default="gemini-2.5-flash", description="Gemini Flash model identifier")
    default_temperature_game_master: float = Field(default=0.3, description="Temperature for Game Master agent")
    default_temperature_threat_actors: float = Field(default=0.7, description="Temperature for threat actor agents")
    
    # Agent Configuration
    max_conversation_turns: int = Field(default=15, description="Maximum turns per scenario")
    default_difficulty_level: int = Field(default=3, description="Starting difficulty level (1-5)")
    target_success_rate: float = Field(default=0.7, description="Target success rate for adaptive difficulty")
    session_timeout_minutes: int = Field(default=30, description="Session timeout in minutes")
    
    # Google Cloud Configuration
    google_cloud_project: Optional[str] = Field(default=None, description="GCP project ID")
    google_cloud_region: str = Field(default="us-central1", description="GCP region")
    vertex_ai_location: str = Field(default="us-central1", description="Vertex AI location")
    
    # Security Configuration
    safe_redirect_base_url: str = Field(
        default="https://cyberguard.academy/safe-redirect", # TODO: find a domain
        description="Base URL for safe phishing link redirects"
    )
    anonymous_user_id_salt: str = Field(
        default="change-this-in-production",
        description="Salt for user ID anonymization"
    )
    
    # Observability Configuration
    cloud_trace_enabled: bool = Field(default=True, description="Enable Cloud Trace")
    structured_logging_enabled: bool = Field(default=True, description="Enable structured logging")
    metrics_collection_enabled: bool = Field(default=True, description="Enable metrics collection")
    
    # Development Configuration
    mock_agents_in_tests: bool = Field(default=True, description="Use mock agents in tests")
    use_local_storage: bool = Field(default=True, description="Use local storage instead of cloud")
    skip_external_apis: bool = Field(default=False, description="Skip external API calls in development")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()