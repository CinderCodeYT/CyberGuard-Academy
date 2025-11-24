"""
Gemini API Client for CyberGuard Academy

Centralized client for interacting with Google's Gemini API.
Provides configured model instances for different agent types.
"""

import os
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from cyberguard.config import settings


class GeminiClient:
    """
    Centralized Gemini API client.
    
    Provides pre-configured model instances for different use cases:
    - Pro model for complex reasoning (Game Master)
    - Flash model for high-volume generation (Threat Actors)
    """
    
    _initialized = False
    _pro_model = None
    _flash_model = None
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize Gemini API with API key from environment."""
        if cls._initialized:
            return
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your API key from: https://aistudio.google.com/app/apikey"
            )
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize models
        cls._pro_model = genai.GenerativeModel(settings.gemini_pro_model)
        cls._flash_model = genai.GenerativeModel(settings.gemini_flash_model)
        
        cls._initialized = True
        print(f"[GeminiClient] Initialized with models: {settings.gemini_pro_model}, {settings.gemini_flash_model}")
    
    @classmethod
    def get_pro_model(cls) -> genai.GenerativeModel:
        """Get Gemini Pro model for complex reasoning tasks."""
        if not cls._initialized:
            cls.initialize()
        return cls._pro_model
    
    @classmethod
    def get_flash_model(cls) -> genai.GenerativeModel:
        """Get Gemini Flash model for high-volume generation."""
        if not cls._initialized:
            cls.initialize()
        return cls._flash_model
    
    @classmethod
    async def generate_text(
        cls,
        prompt: str,
        model_type: str = "flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate text using Gemini API.
        
        Args:
            prompt: The prompt to send to the model
            model_type: "pro" or "flash" (default: "flash")
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_instruction: Optional system instruction for the model
            
        Returns:
            Generated text response
        """
        if not cls._initialized:
            cls.initialize()
        
        # Select model
        model = cls._pro_model if model_type == "pro" else cls._flash_model
        
        # Create generation config
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        try:
            # If system instruction provided, create a new model instance with it
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=settings.gemini_pro_model if model_type == "pro" else settings.gemini_flash_model,
                    system_instruction=system_instruction,
                    generation_config=generation_config
                )
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config if not system_instruction else None
            )
            
            return response.text
            
        except Exception as e:
            print(f"[GeminiClient] Error generating text: {e}")
            raise
    
    @classmethod
    async def generate_with_context(
        cls,
        messages: List[Dict[str, str]],
        model_type: str = "flash",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate text with conversation context.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model_type: "pro" or "flash"
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            system_instruction: Optional system instruction
            
        Returns:
            Generated text response
        """
        if not cls._initialized:
            cls.initialize()
        
        # Convert messages to Gemini format
        # Gemini uses 'user' and 'model' roles
        gemini_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Map roles to Gemini format
            if role in ["user", "human"]:
                gemini_role = "user"
            elif role in ["assistant", "model", "game_master", "agent"]:
                gemini_role = "model"
            else:
                gemini_role = "user"  # Default to user
            
            gemini_messages.append({
                "role": gemini_role,
                "parts": [content]
            })
        
        # Select model
        model = cls._pro_model if model_type == "pro" else cls._flash_model
        
        # Create generation config
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        try:
            # If system instruction provided, create a new model instance
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=settings.gemini_pro_model if model_type == "pro" else settings.gemini_flash_model,
                    system_instruction=system_instruction,
                    generation_config=generation_config
                )
            
            # Start chat with history
            chat = model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Send the last message
            last_message = gemini_messages[-1]["parts"][0] if gemini_messages else "Continue the scenario."
            response = chat.send_message(
                last_message,
                generation_config=generation_config if not system_instruction else None
            )
            
            return response.text
            
        except Exception as e:
            print(f"[GeminiClient] Error generating with context: {e}")
            raise


# Initialize on module import
GeminiClient.initialize()
