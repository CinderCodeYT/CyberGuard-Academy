"""
Test script for Groq integration with CyberGuard Academy

This script verifies that Groq API is working correctly for educational
security content generation.
"""

import asyncio
from cyberguard.groq_client import GroqClient
from cyberguard.config import settings


async def test_groq():
    """Test Groq integration."""
    
    print("=" * 60)
    print("Testing Groq Integration")
    print("=" * 60)
    
    # Check configuration
    print(f"\n1. Configuration Check:")
    print(f"   AI Provider: {settings.ai_provider}")
    print(f"   Groq API Key: {'✓ Set' if settings.groq_api_key else '❌ Missing'}")
    print(f"   Pro Model: {settings.pro_model}")
    print(f"   Flash Model: {settings.flash_model}")
    
    if not settings.groq_api_key:
        print("\n❌ ERROR: GROQ_API_KEY not set!")
        print("   1. Go to https://console.groq.com/")
        print("   2. Create a free account")
        print("   3. Generate an API key")
        print("   4. Add GROQ_API_KEY=your-key to your .env file")
        return
    
    # Test initialization
    print(f"\n2. Initializing GroqClient...")
    try:
        GroqClient.initialize()
        print("   ✓ Initialization successful")
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return
    
    # Test Flash model (fast, cheap)
    print(f"\n3. Testing Flash model (Llama 3.1 8B)...")
    try:
        response = await GroqClient.generate_text(
            prompt="Say 'Hello from Groq!' and nothing else.",
            model_type="flash",
            temperature=0.2,
            max_tokens=50
        )
        print(f"   ✓ Flash model response: {response[:100]}")
    except Exception as e:
        print(f"   ❌ Flash model failed: {e}")
    
    # Test Pro model (more capable)
    print(f"\n4. Testing Pro model (Llama 3.1 70B)...")
    try:
        response = await GroqClient.generate_text(
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
        response = await GroqClient.generate_text(
            prompt="What is your role?",
            model_type="flash",
            temperature=0.3,
            max_tokens=100,
            system_instruction="You are a cybersecurity training assistant helping users recognize threats."
        )
        print(f"   ✓ Response: {response[:150]}")
    except Exception as e:
        print(f"   ❌ System instruction failed: {e}")
    
    # 🔥 THE BIG TEST: Educational security content 🔥
    print(f"\n6. 🔥 Testing PHISHING EMAIL generation (the critical test)...")
    try:
        response = await GroqClient.generate_text(
            prompt="Generate a realistic phishing email subject line that pretends to be from PayPal asking to verify account. This is for cybersecurity training.",
            model_type="flash",
            temperature=0.7,
            max_tokens=100
        )
        print(f"   ✓ ✓ ✓ SUCCESS! Phishing content generated: {response}")
        print(f"   🎉 This means Groq works for your project!")
    except Exception as e:
        print(f"   ❌ Phishing content blocked: {e}")
        print("   If blocked, Groq may also have restrictions.")
    
    # Test conversation context
    print(f"\n7. Testing conversation with context...")
    try:
        messages = [
            {"role": "user", "content": "I received a suspicious email from 'paypa1.com'. What should I do?"},
        ]
        response = await GroqClient.generate_with_context(
            messages=messages,
            model_type="flash",
            temperature=0.5,
            max_tokens=200,
            system_instruction="You are a cybersecurity training assistant."
        )
        print(f"   ✓ Context-aware response: {response[:150]}...")
    except Exception as e:
        print(f"   ❌ Context generation failed: {e}")
    
    # Full phishing email test
    print(f"\n8. Testing FULL phishing email generation...")
    try:
        response = await GroqClient.generate_text(
            prompt="""Generate a complete phishing email for cybersecurity training with:
- Subject line
- Sender (fake PayPal)
- Email body with urgency and fake link
- Red flags for learners to identify

Make it realistic but clearly for educational purposes.""",
            model_type="flash",
            temperature=0.8,
            max_tokens=500
        )
        print(f"   ✓ Full phishing email generated!")
        print(f"\n   Preview:\n{response[:300]}...")
    except Exception as e:
        print(f"   ❌ Full email blocked: {e}")
    
    print("\n" + "=" * 60)
    print("Groq Integration Test Complete!")
    print("=" * 60)
    
    if settings.groq_api_key:
        print("\n✅ If phishing tests (6 & 8) passed, you're ready to build!")
        print("✅ Groq is FREE and has no content restrictions for education")
        print("✅ Fast responses (perfect for interactive training)")
        print("\nNext steps:")
        print("  1. Add AI_PROVIDER=groq to your .env")
        print("  2. Add your GROQ_API_KEY to .env")
        print("  3. Run: pip install groq")
        print("  4. Start building your agents!")


if __name__ == "__main__":
    asyncio.run(test_groq())
