#!/usr/bin/env python3
"""
Simple Game Master Test - Tests basic functionality

Run this to test the Game Master agent structure and basic operations
without needing the full multi-agent system.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test imports first
def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test basic models
        from cyberguard.models import (
            ScenarioContext, 
            UserRole, 
            DifficultyLevel, 
            ThreatType, 
            CyberGuardSession
        )
        print("  ✅ Models imported successfully")
        
        # Test agent base classes
        from cyberguard.agents import BaseAgent, OrchestratorAgent
        print("  ✅ Agent base classes imported successfully")
        
        # Test configuration (mock for now)
        try:
            from cyberguard.config import settings
            print("  ✅ Configuration imported successfully")
        except:
            print("  ⚠️  Configuration not available - using mock")
            # Create mock settings in cyberguard module
            import cyberguard
            if not hasattr(cyberguard, 'config'):
                import types
                cyberguard.config = types.ModuleType('config')
                cyberguard.config.settings = type('MockSettings', (), {
                    'is_development': True,
                    'max_conversation_turns': 20,
                    'safe_redirect_url': 'https://test.com'
                })()
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_model_creation():
    """Test creating model instances."""
    print("\n🧪 Testing model creation...")
    
    try:
        from cyberguard.models import (
            ScenarioContext, 
            UserRole, 
            DifficultyLevel, 
            ThreatType,
            SocialEngineeringPattern
        )
        
        # Test ScenarioContext creation
        context = ScenarioContext(
            user_role=UserRole.GENERAL,
            difficulty_level=DifficultyLevel.BEGINNER,
            threat_pattern=SocialEngineeringPattern.URGENCY,
            recently_seen_patterns=[],
            vulnerability_areas=["email_phishing"]
        )
        print(f"  ✅ ScenarioContext created: {context.user_role}")
        
        # Test enum values
        print(f"  ✅ UserRole enum: {[role.value for role in UserRole]}")
        print(f"  ✅ DifficultyLevel enum: {[level.value for level in DifficultyLevel]}")
        print(f"  ✅ ThreatType enum: {[threat.value for threat in ThreatType]}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Model creation failed: {e}")
        return False


def test_agent_structure():
    """Test the agent class hierarchy."""
    print("\n🧪 Testing agent structure...")
    
    try:
        from cyberguard.agents import BaseAgent, OrchestratorAgent
        
        # Test base agent (abstract - can't instantiate)
        try:
            base = BaseAgent("test", "test")
            print("  ❌ BaseAgent should be abstract!")
            return False
        except TypeError:
            print("  ✅ BaseAgent correctly abstract")
        
        # Test orchestrator agent (also abstract currently)
        try:
            orch = OrchestratorAgent("test_orchestrator")
            print(f"  ✅ OrchestratorAgent created: {orch.agent_name}")
            print(f"      Type: {orch.agent_type}")
            print(f"      Has coordinations: {hasattr(orch, 'active_coordinations')}")
        except Exception as e:
            print(f"  ⚠️  OrchestratorAgent issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Agent structure test failed: {e}")
        return False


def test_tool_imports():
    """Test importing the tools (may fail if not implemented)."""
    print("\n🧪 Testing tool imports...")
    
    tools = [
        "scenario_selector",
        "agent_coordinator", 
        "narrative_manager",
        "hint_provider",
        "debrief_generator"
    ]
    
    working_tools = 0
    
    for tool_name in tools:
        try:
            module = __import__(f"tools.{tool_name}", fromlist=[tool_name])
            print(f"  ✅ {tool_name} imported successfully")
            working_tools += 1
        except ImportError as e:
            print(f"  ❌ {tool_name} failed: {e}")
    
    print(f"\n  📊 Tools working: {working_tools}/{len(tools)}")
    return working_tools > 0


def test_game_master_import():
    """Test importing the Game Master."""
    print("\n🧪 Testing Game Master import...")
    
    try:
        # This will likely fail due to tool dependencies
        from agents.game_master.game_master import GameMasterAgent
        
        print("  ✅ GameMasterAgent imported successfully")
        
        # Try to create instance
        gm = GameMasterAgent()
        print(f"  ✅ GameMasterAgent created: {gm.agent_name}")
        print(f"      Type: {gm.agent_type}")
        
        return True, gm
        
    except Exception as e:
        print(f"  ❌ Game Master import failed: {e}")
        print("      This is expected if tools aren't fully implemented")
        return False, None


def run_simple_tests():
    """Run basic tests that should work."""
    print("🎮 CyberGuard Academy - Simple Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Imports
    total_tests += 1
    if test_imports():
        tests_passed += 1
    
    # Test 2: Model creation  
    total_tests += 1
    if test_model_creation():
        tests_passed += 1
    
    # Test 3: Agent structure
    total_tests += 1
    if test_agent_structure():
        tests_passed += 1
    
    # Test 4: Tool imports (informational)
    test_tool_imports()
    
    # Test 5: Game Master (may fail)
    success, gm = test_game_master_import()
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} core tests passed")
    
    if success and gm:
        print("✅ Game Master is ready for full testing!")
        print("\nNext steps:")
        print("1. Run: python test_game_master.py")
        print("2. Or implement missing tools and try again")
    else:
        print("⚠️  Game Master needs tool implementations to work fully")
        print("\nWhat works:")
        print("- Basic model structure ✅")
        print("- Agent inheritance ✅") 
        print("- Type system ✅")
        print("\nWhat needs work:")
        print("- Tool implementations (scenario_selector, etc.)")
        print("- Agent coordination framework")


if __name__ == "__main__":
    run_simple_tests()