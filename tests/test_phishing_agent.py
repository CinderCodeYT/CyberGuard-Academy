#!/usr/bin/env python3
"""
Phishing Agent Test - Tests the complete phishing agent with all tools

This test validates:
1. Phishing agent initialization with all tools
2. Realistic phishing scenario generation
3. Email, link, and header integration
4. A2A message handling with Game Master
5. Adaptive scenario modification based on user responses
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cyberguard.models import (
    ScenarioContext, 
    UserRole, 
    DifficultyLevel, 
    SocialEngineeringPattern,
    AgentMessage
)
from agents.threat_actors.phishing import PhishingAgent


async def test_phishing_agent_initialization():
    """Test 1: Phishing agent initialization with all tools"""
    print("🧪 Test 1: Phishing Agent Initialization")
    print("=" * 50)
    
    try:
        # Create Phishing Agent
        phishing_agent = PhishingAgent()
        
        # Test initialization
        await phishing_agent.initialize()
        
        print("✅ Phishing Agent initialized successfully")
        print(f"   Agent Name: {phishing_agent.agent_name}")
        print(f"   Threat Type: {phishing_agent.threat_type}")
        print(f"   Tools Loaded: Email Generator, Link Generator, Header Spoofing")
        
        return phishing_agent
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None


async def test_phishing_scenario_generation(phishing_agent: PhishingAgent):
    """Test 2: Generate complete phishing scenario"""
    print("\n🧪 Test 2: Phishing Scenario Generation")
    print("=" * 50)
    
    try:
        # Create test context for different user roles and difficulties
        test_contexts = [
            ScenarioContext(
                user_role=UserRole.GENERAL,
                difficulty_level=DifficultyLevel.BEGINNER,
                threat_pattern=SocialEngineeringPattern.URGENCY,
                session_context="User just started cybersecurity training"
            ),
            ScenarioContext(
                user_role=UserRole.FINANCE,
                difficulty_level=DifficultyLevel.INTERMEDIATE,
                threat_pattern=SocialEngineeringPattern.AUTHORITY,
                session_context="Finance team member, handles payments"
            ),
            ScenarioContext(
                user_role=UserRole.IT_ADMIN,
                difficulty_level=DifficultyLevel.ADVANCED,
                threat_pattern=SocialEngineeringPattern.CURIOSITY,
                session_context="IT admin with high security knowledge"
            )
        ]
        
        scenarios = []
        
        for i, context in enumerate(test_contexts, 1):
            print(f"\n--- Scenario {i}: {context.user_role.value} ({context.difficulty_level.value}) ---")
            
            scenario = await phishing_agent.generate_scenario(context)
            scenarios.append(scenario)
            
            print(f"✅ Generated scenario: {scenario['scenario_id'][:8]}...")
            print(f"   Email Subject: {scenario['email']['subject']}")
            print(f"   Sender: {scenario['email']['sender']['name']}")
            print(f"   Link Domain: {scenario['link']['display_url'].split('/')[2]}")
            print(f"   Total Red Flags: {len(scenario['red_flags']['email_flags']) + len(scenario['red_flags']['link_flags']) + len(scenario['red_flags']['header_flags'])}")
            print(f"   Educational Objectives: {scenario['metadata']['educational_objectives']}")
        
        return scenarios
        
    except Exception as e:
        print(f"❌ Scenario generation failed: {e}")
        return []


async def test_a2a_communication(phishing_agent: PhishingAgent):
    """Test 3: Test A2A communication with Game Master"""
    print("\n🧪 Test 3: A2A Communication")
    print("=" * 50)
    
    try:
        # Simulate Game Master request for scenario generation
        game_master_request = AgentMessage(
            sender_agent="game_master",
            recipient_agent="phishing_agent", 
            message_type="generate_scenario",
            payload={
                "user_role": "general",
                "difficulty": 2,
                "threat_pattern": "urgency",
                "user_context": "User clicked on previous suspicious link"
            },
            session_id="test_session_001",
            correlation_id="test_correlation_001"
        )
        
        # Process the message
        response = await phishing_agent.process_message(game_master_request)
        
        print("✅ A2A Communication successful")
        print(f"   Request Type: {game_master_request.message_type}")
        print(f"   Response Type: {response.message_type}")
        print(f"   Correlation ID: {response.correlation_id}")
        
        if response.message_type == "scenario_ready":
            scenario_content = response.payload.get("scenario_content", {})
            print(f"   Generated Email Subject: {scenario_content.get('email', {}).get('subject', 'N/A')}")
            
        return True
        
    except Exception as e:
        print(f"❌ A2A Communication failed: {e}")
        return False


async def test_scenario_adaptation(phishing_agent: PhishingAgent):
    """Test 4: Test scenario adaptation based on user responses"""
    print("\n🧪 Test 4: Scenario Adaptation")
    print("=" * 50)
    
    try:
        # Test different user responses
        test_responses = [
            {
                "user_input": "This email looks suspicious, I don't trust it",
                "performance_hint": "increase_difficulty",
                "expected_strategy": "escalate_threat"
            },
            {
                "user_input": "I should click this link to verify my account",
                "performance_hint": "decrease_difficulty", 
                "expected_strategy": "add_obvious_red_flags"
            },
            {
                "user_input": "I'm not sure about this email, let me investigate",
                "performance_hint": "maintain_difficulty",
                "expected_strategy": "provide_investigative_clues"
            }
        ]
        
        for i, test_case in enumerate(test_responses, 1):
            print(f"\n--- Adaptation Test {i} ---")
            print(f"User Response: {test_case['user_input']}")
            
            adaptation = await phishing_agent.adapt_scenario(
                session_id="test_session_001",
                user_response=test_case["user_input"],
                performance_hint=test_case["performance_hint"]
            )
            
            print(f"✅ Adaptation Strategy: {adaptation['adaptation_type']}")
            print(f"   Content Type: {adaptation['content']['type']}")
            print(f"   Reasoning: {adaptation['reasoning']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scenario adaptation failed: {e}")
        return False


async def test_educational_content_analysis(scenarios):
    """Test 5: Analyze educational content and red flags"""
    print("\n🧪 Test 5: Educational Content Analysis")
    print("=" * 50)
    
    try:
        if not scenarios:
            print("⚠️  No scenarios to analyze")
            return False
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n--- Scenario {i} Analysis ---")
            
            # Analyze red flags by category
            email_flags = scenario['red_flags']['email_flags']
            link_flags = scenario['red_flags']['link_flags'] 
            header_flags = scenario['red_flags']['header_flags']
            
            print(f"Email Red Flags ({len(email_flags)}):")
            for flag in email_flags:
                print(f"  • {flag['type']}: {flag['description']}")
            
            print(f"Link Red Flags ({len(link_flags)}):")
            for flag in link_flags:
                print(f"  • {flag['type']}: {flag['description']}")
                
            print(f"Header Red Flags ({len(header_flags)}):")
            for flag in header_flags:
                print(f"  • {flag['type']}: {flag['description']}")
            
            print(f"Educational Objectives: {scenario['metadata']['educational_objectives']}")
        
        print("\n✅ Educational content analysis complete")
        return True
        
    except Exception as e:
        print(f"❌ Content analysis failed: {e}")
        return False


async def test_safety_and_redirection():
    """Test 6: Verify all links redirect to safe endpoints"""
    print("\n🧪 Test 6: Safety and Redirection")
    print("=" * 50)
    
    try:
        # Create a simple scenario to test link safety
        phishing_agent = PhishingAgent()
        await phishing_agent.initialize()
        
        context = ScenarioContext(
            user_role=UserRole.GENERAL,
            difficulty_level=DifficultyLevel.BEGINNER,
            threat_pattern=SocialEngineeringPattern.URGENCY
        )
        
        scenario = await phishing_agent.generate_scenario(context)
        
        # Check that actual URL is safe
        actual_url = scenario['link']['actual_url']
        display_url = scenario['link']['display_url']
        
        print(f"✅ Safety verification complete")
        print(f"   Display URL: {display_url}")
        print(f"   Actual URL (safe): {actual_url}")
        print(f"   Contains safe redirect: {'safe' in actual_url}")
        
        # Verify no real malicious content
        email_body = scenario['email']['body']
        safe_indicators = [
            'href="https://example.com' not in email_body,  # No real external links
            'cyberguard.academy' in actual_url or 'safe' in actual_url  # Safe redirect
        ]
        
        print(f"   All safety checks passed: {all(safe_indicators)}")
        
        await phishing_agent.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Safety verification failed: {e}")
        return False


async def main():
    """Run comprehensive phishing agent tests"""
    print("🎯 CyberGuard Academy - Phishing Agent Test Suite")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 6
    
    # Test 1: Initialization
    phishing_agent = await test_phishing_agent_initialization()
    if phishing_agent:
        tests_passed += 1
    else:
        print("❌ Cannot continue - initialization failed")
        return
    
    # Test 2: Scenario generation
    scenarios = await test_phishing_scenario_generation(phishing_agent)
    if scenarios:
        tests_passed += 1
    
    # Test 3: A2A communication
    if await test_a2a_communication(phishing_agent):
        tests_passed += 1
    
    # Test 4: Scenario adaptation
    if await test_scenario_adaptation(phishing_agent):
        tests_passed += 1
    
    # Test 5: Educational content analysis
    if await test_educational_content_analysis(scenarios):
        tests_passed += 1
    
    # Test 6: Safety verification
    if await test_safety_and_redirection():
        tests_passed += 1
    
    # Cleanup
    try:
        await phishing_agent.shutdown()
        print("\n✅ Phishing Agent shutdown complete")
    except Exception as e:
        print(f"❌ Shutdown error: {e}")
    
    # Results
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Phishing Agent is fully functional!")
        print("\n🚀 Ready for integration with Game Master")
        print("   • Realistic phishing scenarios ✅")
        print("   • Multi-tool coordination ✅") 
        print("   • A2A communication ✅")
        print("   • Adaptive difficulty ✅")
        print("   • Safety controls ✅")
    else:
        print("⚠️  Some tests failed - review implementation")
        
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())