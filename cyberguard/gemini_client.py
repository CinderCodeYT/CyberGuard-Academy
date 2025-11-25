"""
AI Client for CyberGuard Academy

Unified client supporting multiple AI providers:
- Groq (recommended): Fast, free, permissive for educational content
- Vertex AI: Enterprise option with GCP integration

Provides configured model instances for different agent types.
"""

from __future__ import annotations

import os
from typing import Optional, Dict, Any, List

# Groq imports - only if needed
GROQ_AVAILABLE = False
VERTEX_AVAILABLE = False

from cyberguard.config import settings


class GeminiClient:
    """
    Unified AI client supporting multiple providers.
    
    Provides pre-configured model instances for different use cases:
    - Pro model for complex reasoning (Game Master)
    - Flash model for high-volume generation (Threat Actors)
    
    Provider selection based on settings.ai_provider:
    - 'groq': Free, fast, permissive (recommended for development)
    - 'vertex': Enterprise GCP option
    """
    
    _initialized = False
    _provider = None
    _groq_client = None
    _pro_model = None
    _flash_model = None
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize AI client based on configured provider."""
        if cls._initialized:
            return
        
        cls._provider = settings.ai_provider.lower()
        
        if cls._provider == "groq":
            cls._initialize_groq()
        elif cls._provider == "vertex":
            cls._initialize_vertex()
        else:
            raise ValueError(f"Unknown AI provider: {cls._provider}. Must be 'groq' or 'vertex'")
        
        cls._initialized = True
    
    @classmethod
    def _initialize_groq(cls) -> None:
        """Initialize Groq client."""
        global GROQ_AVAILABLE
        try:
            from groq import Groq
            GROQ_AVAILABLE = True
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
        print(f"[GeminiClient] Initialized Groq with models: {settings.pro_model}, {settings.flash_model}")
    
    @classmethod
    def _initialize_vertex(cls) -> None:
        """Initialize Vertex AI client."""
        global VERTEX_AVAILABLE
        try:
            from vertexai.generative_models import GenerativeModel
            import vertexai
            VERTEX_AVAILABLE = True
        except ImportError:
            raise ImportError("Vertex AI SDK not installed. Run: pip install google-cloud-aiplatform")
        
        project_id = settings.google_cloud_project
        location = settings.vertex_ai_location
        
        if not project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT not found in environment. "
                "Please set it in your .env file to your GCP project ID."
            )
        
        vertexai.init(project=project_id, location=location)
        cls._pro_model = GenerativeModel(settings.pro_model)
        cls._flash_model = GenerativeModel(settings.flash_model)
        print(f"[GeminiClient] Initialized Vertex AI in project '{project_id}' with models: {settings.pro_model}, {settings.flash_model}")
    
    @classmethod
    def get_pro_model(cls):
        """Get Pro model for complex reasoning tasks."""
        if not cls._initialized:
            cls.initialize()
        if cls._provider == "groq":
            return cls._groq_client
        return cls._pro_model
    
    @classmethod
    def get_flash_model(cls):
        """Get Flash model for high-volume generation."""
        if not cls._initialized:
            cls.initialize()
        if cls._provider == "groq":
            return cls._groq_client
        return cls._flash_model
    
    @classmethod
    def _get_safety_settings(cls) -> List[Any]:
        """
        Get safety settings for educational security content.
        
        Vertex AI allows BLOCK_NONE for all categories, which is critical
        for generating realistic phishing and social engineering scenarios
        for training purposes.
        """
        # Lazy import Vertex AI types
        from vertexai.generative_models import SafetySetting, HarmCategory, HarmBlockThreshold
        
        return [
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
            SafetySetting(
                category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=HarmBlockThreshold.BLOCK_NONE
            ),
        ]
    
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
        Generate text using configured AI provider.
        
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
        
        if cls._provider == "groq":
            return await cls._generate_text_groq(
                prompt, model_type, temperature, max_tokens, system_instruction
            )
        else:
            return await cls._generate_text_vertex(
                prompt, model_type, temperature, max_tokens, system_instruction
            )
    
    @classmethod
    async def _generate_text_groq(
        cls,
        prompt: str,
        model_type: str,
        temperature: float,
        max_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate text using Groq."""
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
            print(f"[GeminiClient] Groq error: {e}")
            raise
    
    @classmethod
    async def _generate_text_vertex(
        cls,
        prompt: str,
        model_type: str,
        temperature: float,
        max_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate text using Vertex AI."""
        from vertexai.generative_models import GenerativeModel, GenerationConfig
        
        base_model_name = settings.pro_model if model_type == "pro" else settings.flash_model
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        try:
            # Create model with system instruction if provided
            if system_instruction:
                model = GenerativeModel(
                    base_model_name,
                    system_instruction=[system_instruction]
                )
            else:
                model = cls._pro_model if model_type == "pro" else cls._flash_model
            
            # Generate response with permissive safety settings
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=cls._get_safety_settings()
            )
            
            # Check if response was blocked
            if not response.candidates:
                print(f"[GeminiClient] No candidates returned")
                raise ValueError("Content generation failed: No candidates returned")
            
            candidate = response.candidates[0]
            
            # Check if we have content parts
            if not candidate.content or not candidate.content.parts:
                finish_reason = candidate.finish_reason if hasattr(candidate, 'finish_reason') else 'unknown'
                print(f"[GeminiClient] Empty response. Finish reason: {finish_reason}")
                if hasattr(candidate, 'safety_ratings'):
                    print(f"[GeminiClient] Safety ratings: {candidate.safety_ratings}")
                raise ValueError(f"Content blocked or empty (finish_reason: {finish_reason})")
            
            # Extract text from parts
            if candidate.content and candidate.content.parts:
                return candidate.content.parts[0].text
            else:
                # Empty response but finish_reason is MAX_TOKENS - return empty string
                return ""
            
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
        
        if cls._provider == "groq":
            return await cls._generate_with_context_groq(
                messages, model_type, temperature, max_tokens, system_instruction
            )
        else:
            return await cls._generate_with_context_vertex(
                messages, model_type, temperature, max_tokens, system_instruction
            )
    
    @classmethod
    async def _generate_with_context_groq(
        cls,
        messages: List[Dict[str, str]],
        model_type: str,
        temperature: float,
        max_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate with context using Groq."""
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
            print(f"[GeminiClient] Groq context error: {e}")
            raise
    
    @classmethod
    async def _generate_with_context_vertex(
        cls,
        messages: List[Dict[str, str]],
        model_type: str,
        temperature: float,
        max_tokens: int,
        system_instruction: Optional[str]
    ) -> str:
        """Generate chat response using Vertex AI."""
        from vertexai.generative_models import GenerativeModel, GenerationConfig, Content, Part
        
        base_model_name = settings.pro_model if model_type == "pro" else settings.flash_model
        
        # Convert messages to Vertex AI format
        vertex_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Map roles to Vertex AI format
            if role in ["user", "human"]:
                vertex_role = "user"
            elif role in ["assistant", "model", "game_master", "agent"]:
                vertex_role = "model"
            else:
                vertex_role = "user"
            
            vertex_messages.append(
                Content(
                    role=vertex_role,
                    parts=[Part.from_text(content)]
                )
            )
        
        # Select base model name
        base_model_name = settings.gemini_pro_model if model_type == "pro" else settings.gemini_flash_model
        
        # Create generation config
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        try:
            # Create model with system instruction if provided
            if system_instruction:
                model = GenerativeModel(
                    base_model_name,
                    system_instruction=[system_instruction]
                )
            else:
                model = cls._pro_model if model_type == "pro" else cls._flash_model
            
            # Start chat with history
            # Disable response validation to handle finish_reason=MAX_TOKENS gracefully
            chat = model.start_chat(
                history=vertex_messages[:-1] if len(vertex_messages) > 1 else [],
                response_validation=False
            )
            
            # Send the last message
            last_message = vertex_messages[-1].parts[0].text if vertex_messages else "Continue the scenario."
            response = chat.send_message(
                last_message,
                generation_config=generation_config,
                safety_settings=cls._get_safety_settings()
            )

            # Check response
            if not response.candidates:
                print(f"[GeminiClient] No candidates returned in chat")
                raise ValueError("Chat generation failed: No candidates returned")
            
            candidate = response.candidates[0]
            
            if not candidate.content or not candidate.content.parts:
                finish_reason = candidate.finish_reason if hasattr(candidate, 'finish_reason') else 'unknown'
                print(f"[GeminiClient] Empty chat response. Finish reason: {finish_reason}")
                raise ValueError(f"Content blocked or empty in chat (finish_reason: {finish_reason})")
            
            return candidate.content.parts[0].text
            
        except Exception as e:
            print(f"[GeminiClient] Error generating with context: {e}")
            raise
