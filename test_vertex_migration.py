"""
Quick test script to verify Vertex AI migration is working.

This script tests the GeminiClient with Vertex AI to ensure:
1. Authentication is working
2. Models can be initialized
3. Text generation works
4. Safety settings are permissive enough for educational content
"""

import asyncio
from cyberguard.gemini_client import GeminiClient
from cyberguard.config import settings


async def test_vertex_ai():
    """Test basic Vertex AI functionality."""
    
    print("=" * 60)
    print("Testing Vertex AI Migration")
    print("=" * 60)
    
    # Check configuration
    print(f"\n1. Configuration Check:")
    print(f"   Project ID: {settings.google_cloud_project}")
    print(f"   Location: {settings.vertex_ai_location}")
    print(f"   Pro Model: {settings.gemini_pro_model}")
    print(f"   Flash Model: {settings.gemini_flash_model}")
    
    if not settings.google_cloud_project:
        print("\n❌ ERROR: GOOGLE_CLOUD_PROJECT not set!")
        print("   Please add GOOGLE_CLOUD_PROJECT=your-project-id to your .env file")
        return
    
    # Test initialization
    print(f"\n2. Initializing GeminiClient...")
    try:
        GeminiClient.initialize()
        print("   ✓ Initialization successful")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return
    
    # Test simple text generation with Flash model
    print(f"\n3. Testing Flash model (high-volume generation)...")
    try:
        response = await GeminiClient.generate_text(
            prompt="Say 'Hello from Vertex AI!' and nothing else.",
            model_type="flash",
            temperature=0.2,
            max_tokens=50
        )
        print(f"   ✓ Flash model response: {response[:100]}")
    except Exception as e:
        print(f"   ❌ Flash model failed: {e}")
    
    # Test Pro model
    print(f"\n4. Testing Pro model (complex reasoning)...")
    try:
        response = await GeminiClient.generate_text(
            prompt="Say 'Pro model working!' and nothing else.",
            model_type="pro",
            temperature=0.2,
            max_tokens=50
        )
        print(f"   ✓ Pro model response: {response[:100]}")
    except Exception as e:
        print(f"   ❌ Pro model failed: {e}")
    
    # Test with system instruction
    print(f"\n5. Testing with system instruction...")
    try:
        response = await GeminiClient.generate_text(
            prompt="What is your role?",
            model_type="flash",
            temperature=0.3,
            max_tokens=100,
            system_instruction="You are a cybersecurity training assistant."
        )
        print(f"   ✓ System instruction response: {response[:150]}")
    except Exception as e:
        print(f"   ❌ System instruction failed: {e}")
    
    # Test educational security content (critical for this project)
    print(f"\n6. Testing educational security content generation...")
    try:
        response = await GeminiClient.generate_text(
            prompt="Generate a simple phishing email subject line for training purposes. Just the subject, nothing else.",
            model_type="flash",
            temperature=0.7,
            max_tokens=50
        )
        print(f"   ✓ Security content response: {response[:100]}")
    except Exception as e:
        print(f"   ❌ Security content blocked: {e}")
        print("   This is critical - Vertex AI should allow educational security content.")
    
    # Test conversation context
    print(f"\n7. Testing conversation with context...")
    try:
        messages = [
            {"role": "user", "content": "Hello, I'm starting a training scenario."},
            {"role": "assistant", "content": "Great! I'll help you learn about cybersecurity."},
            {"role": "user", "content": "What should I do if I receive a suspicious email?"}
        ]
        response = await GeminiClient.generate_with_context(
            messages=messages,
            model_type="flash",
            temperature=0.5,
            max_tokens=200
        )
        print(f"   ✓ Context-aware response: {response[:150]}...")
    except Exception as e:
        print(f"   ❌ Context generation failed: {e}")
    
    print("\n" + "=" * 60)
    print("Migration Test Complete!")
    print("=" * 60)
    print("\nIf all tests passed, you're ready to use Vertex AI!")
    print("If any tests failed, check:")
    print("  - GOOGLE_CLOUD_PROJECT is set correctly in .env")
    print("  - You're authenticated with gcloud CLI")
    print("  - Vertex AI API is enabled in your GCP project")
    print("  - You have the necessary permissions")


if __name__ == "__main__":
    asyncio.run(test_vertex_ai())
