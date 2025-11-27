"""
AI Client for CyberGuard Academy

Unified client supporting Groq:
- Groq (recommended): Fast, free, permissive for educational content

Provides configured model instances for different agent types.
"""

from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

from cyberguard.config import settings

class GroqClient:
    """
    AI client for Groq provider.
    
    Provides pre-configured model instances for different use cases:
    - Pro model for complex reasoning (Game Master)
    - Flash model for high-volume generation (Threat Actors)
    """
    
    _initialized = False
    _groq_client = None
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize Groq client."""
        if cls._initialized:
            return
        
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("Groq SDK not installed. Run: pip install groq")
        
        api_key = settings.groq_api_key
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your free API key from: https://console.groq.com/"
            )
        
        cls._groq_client = Groq(api_key=api_key)
        print(f"[GroqClient] Initialized Groq with models: {settings.pro_model}, {settings.flash_model}")
        
        cls._initialized = True
    
    @classmethod
    def get_client(cls):
        """Get the underlying Groq client."""
        if not cls._initialized:
            cls.initialize()
        return cls._groq_client
    
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
        Generate text using Groq.
        
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
        
        model_name = settings.pro_model if model_type == "pro" else settings.flash_model
        
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            
            response = cls._groq_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[GroqClient] Groq error: {e}")
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
        Generate text with conversation context using Groq.
        
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
        
        model_name = settings.pro_model if model_type == "pro" else settings.flash_model
        
        try:
            # Convert messages to Groq format
            groq_messages = []
            if system_instruction:
                groq_messages.append({"role": "system", "content": system_instruction})
            
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Map roles to standard format
                if role in ["user", "human"]:
                    groq_role = "user"
                elif role in ["assistant", "model", "game_master", "agent"]:
                    groq_role = "assistant"
                else:
                    groq_role = "user"
                
                groq_messages.append({"role": groq_role, "content": content})
            
            response = cls._groq_client.chat.completions.create(
                model=model_name,
                messages=groq_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[GroqClient] Groq context error: {e}")
            raise
