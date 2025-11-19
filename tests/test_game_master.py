#!/usr/bin/env python3
"""
Manual Testing Script for Game Master Agent

This script allows you to manually test the Game Master agent and its tools
without needing a full multi-agent system running.
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
    ThreatType,
    SocialEngineeringPattern
)
from agents.game_master.game_master import GameMasterAgent


async def test_basic_initialization():
    """Test 1: Basic Game Master initialization"""
    print("🧪 Test 1: Game Master Initialization")
    print("=" * 50)
    
    try:
        # Create Game Master
        game_master = GameMasterAgent()
        
        # Test initialization
        await game_master.initialize()
        
        print("✅ Game Master initialized successfully")
        return game_master
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return None


async def test_scenario_creation(game_master: GameMasterAgent):
    """Test 2: Create a basic training scenario"""
    print("\n🧪 Test 2: Scenario Creation")
    print("=" * 50)
    
    try:
        # Create test context
        context = ScenarioContext(
            user_role=UserRole.GENERAL,
            difficulty_level=DifficultyLevel.BEGINNER,
            threat_pattern=SocialEngineeringPattern.URGENCY,
            recently_seen_patterns=[],
            vulnerability_areas=["email_phishing"]
        )
        
        # Start scenario
        session = await game_master.start_scenario(
            user_id="test_user_001",
            scenario_type="phishing",
            context=context
        )
        
        print(f"✅ Scenario created: {session.session_id}")
        print(f"   Type: {session.scenario_type}")
        print(f"   User Role: {session.user_role}")
        print(f"   Difficulty: {session.current_difficulty}")
        
        return session
        
    except Exception as e:
        print(f"❌ Scenario creation failed: {e}")
        return None


async def test_user_interaction(game_master: GameMasterAgent, session):
    """Test 3: Simulate user interaction"""
    print("\n🧪 Test 3: User Interaction")
    print("=" * 50)
    
    try:
        # Test user responses
        test_responses = [
            "I received an email asking me to verify my password",
            "The email looks legitimate and came from IT support",
            "I think I should click the link to verify my account"
        ]
        
        for i, user_input in enumerate(test_responses, 1):
            print(f"\n👤 User Input {i}: {user_input}")
            
            response = await game_master.handle_user_response(
                session_id=session.session_id,
                user_input=user_input
            )
            
            print(f"🤖 Game Master Response: {response['content'][:200]}...")
            print(f"   Session State: {response['session_state']}")
            
            if response.get('scenario_complete'):
                print("   ✅ Scenario completed!")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ User interaction failed: {e}")
        return False


async def test_session_management(game_master: GameMasterAgent):
    """Test 4: Session management features"""
    print("\n🧪 Test 4: Session Management")
    print("=" * 50)
    
    try:
        # List active sessions
        sessions = game_master.list_active_sessions()
        print(f"✅ Active sessions: {len(sessions)}")
        
        for session in sessions:
            print(f"   Session: {session['session_id']}")
            print(f"   Duration: {session.get('duration_seconds', 0)}s")
            print(f"   Turns: {session['conversation_turns']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Session management failed: {e}")
        return False


async def test_tools_individually():
    """Test 5: Test individual tools in isolation"""
    print("\n🧪 Test 5: Individual Tool Testing")
    print("=" * 50)
    
    # Test ScenarioSelector
    try:
        from tools.scenario_selector import ScenarioSelector
        
        selector = ScenarioSelector()
        await selector.initialize()
        
        scenario = await selector.select_scenario(
            user_role=UserRole.GENERAL,
            difficulty_level=DifficultyLevel.BEGINNER,
            threat_type="phishing",
            recently_seen_patterns=[],
            vulnerability_areas=["email_phishing"]
        )
        
        print("✅ ScenarioSelector working")
        print(f"   Selected: {scenario.get('title', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ ScenarioSelector failed: {e}")
    
    # Test other tools similarly...
    try:
        from tools.narrative_manager import NarrativeManager
        
        narrative = NarrativeManager()
        await narrative.initialize()
        
        opening = await narrative.generate_opening(
            scenario_details={"title": "Test Scenario"},
            user_context=ScenarioContext(
                user_role=UserRole.GENERAL,
                difficulty_level=DifficultyLevel.BEGINNER,
                threat_pattern=SocialEngineeringPattern.URGENCY
            )
        )
        
        print("✅ NarrativeManager working")
        print(f"   Generated: {opening[:100]}...")
        
    except Exception as e:
        print(f"❌ NarrativeManager failed: {e}")


async def interactive_test():
    """Interactive testing mode - chat with Game Master"""
    print("\n🧪 Interactive Test Mode")
    print("=" * 50)
    print("Type 'quit' to exit\n")
    
    # Initialize Game Master
    game_master = GameMasterAgent()
    await game_master.initialize()
    
    # Create context
    context = ScenarioContext(
        user_role=UserRole.GENERAL,
        difficulty_level=DifficultyLevel.BEGINNER,
        threat_pattern=SocialEngineeringPattern.URGENCY
    )
    
    # Start scenario
    session = await game_master.start_scenario(
        user_id="interactive_user",
        scenario_type="phishing",
        context=context
    )
    
    print("🤖 Game Master: Scenario started! What would you like to do?")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'stop']:
                break
                
            response = await game_master.handle_user_response(
                session_id=session.session_id,
                user_input=user_input
            )
            
            print(f"\n🤖 Game Master: {response['content']}")
            
            if response.get('scenario_complete'):
                print("\n✅ Scenario completed!")
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all tests or interactive mode"""
    print("🎮 CyberGuard Academy - Game Master Test Suite")
    print("=" * 60)
    
    # Check if interactive mode requested
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        await interactive_test()
        return
    
    # Run automated tests
    print("Running automated tests...\n")
    
    # Test 1: Initialization
    game_master = await test_basic_initialization()
    if not game_master:
        print("❌ Cannot continue - initialization failed")
        return
    
    # Test 2: Scenario creation  
    session = await test_scenario_creation(game_master)
    if not session:
        print("❌ Cannot continue - scenario creation failed")
        return
    
    # Test 3: User interaction
    interaction_success = await test_user_interaction(game_master, session)
    
    # Test 4: Session management
    await test_session_management(game_master)
    
    # Test 5: Individual tools
    await test_tools_individually()
    
    # Cleanup
    try:
        await game_master.shutdown()
        print("\n✅ Game Master shutdown complete")
    except Exception as e:
        print(f"❌ Shutdown error: {e}")
    
    print("\n🎯 Test Suite Complete!")
    print("=" * 60)
    print("To run interactive mode: python test_game_master.py interactive")


if __name__ == "__main__":
    asyncio.run(main())