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
    environment: str = Field(default="production", description="Deployment environment")
    debug: bool = Field(default=True, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # AI Provider Configuration
    ai_provider: str = Field(default="groq", description="AI provider: 'groq' or 'vertex'")
    groq_api_key: str = Field(default="", description="Groq API key")
    
    # Google Cloud Configuration (for Vertex AI)
    google_cloud_project: str = Field(default="", description="GCP project ID")
    google_cloud_region: str = Field(default="us-central1", description="GCP region")
    vertex_ai_location: str = Field(default="us-central1", description="Vertex AI location")
    
    # Model Configuration
    # For Groq: llama-3.3-70b-versatile (pro), llama-3.1-8b-instant (flash)
    # For Vertex: gemini-2.5-pro, gemini-2.5-flash
    pro_model: str = Field(default="llama-3.3-70b-versatile", description="Pro model for complex reasoning")
    flash_model: str = Field(default="llama-3.1-8b-instant", description="Flash model for high-volume generation")
    default_temperature_game_master: float = Field(default=0.3, description="Temperature for Game Master agent")
    default_temperature_threat_actors: float = Field(default=0.7, description="Temperature for threat actor agents")
    
    # Agent Configuration
    max_conversation_turns: int = Field(default=25, description="Maximum turns per scenario")
    default_difficulty_level: int = Field(default=3, description="Starting difficulty level (1-5)")
    target_success_rate: float = Field(default=0.7, description="Target success rate for adaptive difficulty")
    session_timeout_minutes: int = Field(default=30, description="Session timeout in minutes")
    
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