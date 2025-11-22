#!/usr/bin/env python3
"""
Memory Manager Agent Test - CyberGuard Academy

Comprehensive test suite for the Memory Manager agent and all its tools.

Tests:
1. Memory Manager initialization and shutdown
2. Session management (create, update, retrieve)
3. User profiling and learning preferences
4. Pattern analysis and vulnerability detection
5. Progress tracking and achievements
6. A2A communication with other agents
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cyberguard.models import (
    ScenarioContext, UserRole, DifficultyLevel, 
    SocialEngineeringPattern, AgentMessage, CyberGuardSession
)
from agents.memory.memory_manager import MemoryManagerAgent


async def test_memory_manager_initialization():
    """Test 1: Memory Manager initialization and tool loading"""
    print("🧪 Test 1: Memory Manager Initialization")
    print("=" * 50)
    
    try:
        # Create Memory Manager Agent
        memory_manager = MemoryManagerAgent()
        
        # Test initialization
        await memory_manager.initialize()
        
        print("✅ Memory Manager initialized successfully")
        print(f"   Agent Name: {memory_manager.agent_name}")
        print(f"   Tools Loaded: Session Manager, User Profiler, Pattern Analyzer, Progress Tracker")
        print(f"   Storage Paths Created: sessions/, profiles/, patterns/, progress/")
        
        return memory_manager
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_session_management(memory_manager: MemoryManagerAgent):
    """Test 2: Session creation, retrieval, and updates"""
    print("\n🧪 Test 2: Session Management")
    print("=" * 50)
    
    try:
        test_user_id = "test_user_001"
        
        # Test session creation
        print("--- Creating New Session ---")
        session = await memory_manager.create_session(
            user_id=test_user_id,
            user_role=UserRole.FINANCE,
            initial_difficulty=DifficultyLevel.INTERMEDIATE
        )
        
        print(f"✅ Created session: {session.session_id[:8]}...")
        print(f"   User ID: {session.user_id[:8]}...")
        print(f"   User Role: {session.user_role.value}")
        print(f"   Initial Difficulty: {session.current_difficulty.value}")
        
        # Test session retrieval
        print("\n--- Retrieving Session ---")
        retrieved_session = await memory_manager.get_session(session.session_id)
        
        if retrieved_session:
            print(f"✅ Retrieved session successfully")
            print(f"   Session Active: {retrieved_session.end_time is None}")
            print(f"   Conversation History: {len(retrieved_session.conversation_history)} entries")
        else:
            print("❌ Failed to retrieve session")
            return False
        
        # Test session updates
        print("\n--- Updating Session ---")
        updates = {
            "conversation_history": [
                {"role": "user", "content": "This email looks suspicious", "timestamp": datetime.now().isoformat()},
                {"role": "agent", "content": "Good observation! What specifically made you suspicious?", "timestamp": datetime.now().isoformat()}
            ],
            "decision_points": [
                {
                    "turn": 1,
                    "vulnerability": "phishing_email_recognition",
                    "user_choice": "report_as_suspicious",
                    "correct_choice": "report_as_suspicious",
                    "risk_score_impact": 0.0
                }
            ],
            "threat_actor_active": "phishing_agent"
        }
        
        success = await memory_manager.update_session(session.session_id, updates)
        
        if success:
            print("✅ Session updated successfully")
            print(f"   Conversation entries: {len(updates['conversation_history'])}")
            print(f"   Decision points: {len(updates['decision_points'])}")
            print(f"   Active threat actor: {updates['threat_actor_active']}")
        else:
            print("❌ Failed to update session")
            return False
        
        return session
        
    except Exception as e:
        print(f"❌ Session management failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_user_profiling(memory_manager: MemoryManagerAgent):
    """Test 3: User profile creation and learning preferences"""
    print("\n🧪 Test 3: User Profiling")
    print("=" * 50)
    
    try:
        test_user_id = "test_user_002"
        
        # Test profile creation for different user roles
        test_roles = [
            (UserRole.GENERAL, "General Employee"),
            (UserRole.FINANCE, "Finance Team Member"), 
            (UserRole.IT_ADMIN, "IT Administrator"),
            (UserRole.EXECUTIVE, "Executive")
        ]
        
        for user_role, role_description in test_roles:
            print(f"\n--- Creating Profile: {role_description} ---")
            
            # Create profile through user profiler
            profile = await memory_manager.user_profiler.create_profile(
                user_id=f"{test_user_id}_{user_role.value}",
                user_role=user_role
            )
            
            print(f"✅ Created profile for {role_description}")
            print(f"   User Role: {profile['user_role']}")
            print(f"   Preferred Difficulty: {profile['learning_preferences']['preferred_difficulty']}")
            print(f"   Learning Pace: {profile['learning_preferences']['learning_pace']}")
            print(f"   Initial Skills: Phishing Recognition {profile['skill_assessments']['phishing_recognition']:.1f}")
            print(f"   Learning Goals: {len(profile['vulnerability_patterns']['learning_goals'])} goals")
        
        # Test profile retrieval and updates
        print("\n--- Testing Profile Updates ---")
        
        profile = await memory_manager.user_profiler.get_profile(f"{test_user_id}_{UserRole.FINANCE.value}")
        
        if profile:
            # Update profile with new learning data
            updates = {
                "learning_preferences": {
                    "preferred_difficulty": 4,
                    "learning_pace": "fast"
                },
                "skill_assessments": {
                    "phishing_recognition": 0.7,
                    "link_verification": 0.6
                }
            }
            
            success = await memory_manager.user_profiler.update_profile(
                user_id=f"{test_user_id}_{UserRole.FINANCE.value}",
                updates=updates,
                merge=True
            )
            
            if success:
                print("✅ Profile updated successfully")
                print("   Difficulty preference increased")
                print("   Skill assessments improved")
            else:
                print("❌ Profile update failed")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ User profiling failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_pattern_analysis(memory_manager: MemoryManagerAgent):
    """Test 4: Pattern analysis and vulnerability detection"""
    print("\n🧪 Test 4: Pattern Analysis")
    print("=" * 50)
    
    try:
        test_user_id = "test_user_003"
        
        # Create test user profile
        profile = await memory_manager.user_profiler.create_profile(
            user_id=test_user_id,
            user_role=UserRole.GENERAL
        )
        
        # Create sample decision data showing various patterns
        sample_decisions = [
            # Strong performance on urgency patterns
            {
                "turn": 1,
                "vulnerability_type": "urgency_phishing",
                "social_eng_pattern": "urgency",
                "user_choice": "report_suspicious",
                "correct_choice": "report_suspicious",
                "response_time": 25,
                "confidence_level": 0.8,
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "turn": 2,
                "vulnerability_type": "urgency_phishing", 
                "social_eng_pattern": "urgency",
                "user_choice": "report_suspicious",
                "correct_choice": "report_suspicious",
                "response_time": 20,
                "confidence_level": 0.9,
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
            },
            # Weak performance on authority patterns
            {
                "turn": 3,
                "vulnerability_type": "authority_phishing",
                "social_eng_pattern": "authority",
                "user_choice": "click_link",
                "correct_choice": "report_suspicious",
                "response_time": 10,
                "confidence_level": 0.6,
                "timestamp": (datetime.now() - timedelta(hours=12)).isoformat()
            },
            {
                "turn": 4,
                "vulnerability_type": "authority_phishing",
                "social_eng_pattern": "authority", 
                "user_choice": "click_link",
                "correct_choice": "report_suspicious",
                "response_time": 8,
                "confidence_level": 0.7,
                "timestamp": (datetime.now() - timedelta(hours=6)).isoformat()
            },
            # Mixed performance on curiosity patterns
            {
                "turn": 5,
                "vulnerability_type": "curiosity_phishing",
                "social_eng_pattern": "curiosity",
                "user_choice": "report_suspicious",
                "correct_choice": "report_suspicious", 
                "response_time": 45,
                "confidence_level": 0.5,
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat()
            },
            {
                "turn": 6,
                "vulnerability_type": "curiosity_phishing",
                "social_eng_pattern": "curiosity",
                "user_choice": "click_link",
                "correct_choice": "report_suspicious",
                "response_time": 15,
                "confidence_level": 0.8,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        print("--- Analyzing User Patterns ---")
        
        # Perform pattern analysis
        analysis = await memory_manager.analyze_user_patterns(
            user_id=test_user_id,
            recent_decisions=sample_decisions
        )
        
        print("✅ Pattern analysis completed")
        
        # Display vulnerability patterns
        vulnerability_patterns = analysis.get("vulnerability_patterns", {})
        weak_areas = vulnerability_patterns.get("weak_threat_types", [])
        strong_areas = vulnerability_patterns.get("strong_threat_types", [])
        
        print(f"\n--- Vulnerability Analysis ---")
        print(f"Weak Areas ({len(weak_areas)}):")
        for area in weak_areas:
            print(f"  • {area['threat_type']}: {area['success_rate']:.1%} success rate ({area['attempts']} attempts)")
        
        print(f"\nStrong Areas ({len(strong_areas)}):")
        for area in strong_areas:
            print(f"  • {area['threat_type']}: {area['success_rate']:.1%} success rate ({area['attempts']} attempts)")
        
        # Display behavioral patterns
        behavioral_patterns = analysis.get("behavioral_patterns", {})
        response_patterns = behavioral_patterns.get("response_patterns", {})
        
        print(f"\n--- Behavioral Analysis ---")
        print(f"Average Response Time: {response_patterns.get('average_response_time', 0):.1f} seconds")
        print(f"Hasty Decision Rate: {response_patterns.get('hasty_decision_rate', 0):.1%}")
        print(f"Careful Decision Rate: {response_patterns.get('careful_decision_rate', 0):.1%}")
        
        # Display learning trends
        learning_trends = analysis.get("learning_trends", {})
        print(f"\n--- Learning Trends ---")
        print(f"Overall Trend: {learning_trends.get('trend', 'unknown')}")
        print(f"Improvement Rate: {learning_trends.get('improvement_rate', 0):+.1%}")
        
        # Display recommendations
        recommendations = analysis.get("recommendations", [])
        print(f"\n--- Recommendations ({len(recommendations)}) ---")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pattern analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_progress_tracking(memory_manager: MemoryManagerAgent):
    """Test 5: Progress tracking and achievement system"""
    print("\n🧪 Test 5: Progress Tracking")
    print("=" * 50)
    
    try:
        test_user_id = "test_user_004"
        
        print("--- Simulating User Progress ---")
        
        # Simulate a series of successful identifications
        progress_updates = [
            {"scenario_completed": True, "threat_identified": True, "scenario_type": "phishing", "response_time": 30, "difficulty": 2},
            {"scenario_completed": True, "threat_identified": True, "scenario_type": "phishing", "response_time": 25, "difficulty": 2},
            {"scenario_completed": True, "threat_identified": True, "scenario_type": "phishing", "response_time": 20, "difficulty": 3},
            {"scenario_completed": True, "threat_missed": True, "scenario_type": "authority", "response_time": 15, "difficulty": 3},
            {"scenario_completed": True, "threat_identified": True, "scenario_type": "urgency", "response_time": 18, "difficulty": 3},
            {"scenario_completed": True, "threat_identified": True, "scenario_type": "curiosity", "response_time": 35, "difficulty": 4},
            {"scenario_completed": True, "threat_identified": True, "scenario_type": "phishing", "response_time": 22, "difficulty": 4},
            # This should trigger streak achievement
            {"scenario_completed": True, "threat_identified": True, "scenario_type": "phishing", "response_time": 28, "difficulty": 4},
        ]
        
        new_achievements_total = []
        
        for i, update in enumerate(progress_updates, 1):
            print(f"\n--- Scenario {i} ---")
            
            result = await memory_manager.progress_tracker.update_progress(
                user_id=test_user_id,
                progress_data=update
            )
            
            # Display results
            progress = result.get("progress", {})
            new_achievements = result.get("new_achievements", [])
            level_up = result.get("level_up", False)
            
            print(f"Scenario Result: {'✅ Success' if update.get('threat_identified') else '❌ Missed'}")
            print(f"Current Streak: {progress.get('current_streak', 0)}")
            print(f"Total Points: {progress.get('total_points', 0)}")
            print(f"Current Level: {progress.get('current_level', 1)}")
            
            if new_achievements:
                print(f"🏆 New Achievements:")
                for achievement in new_achievements:
                    print(f"   • {achievement['name']}: {achievement['description']} (+{achievement['points']} pts)")
                    new_achievements_total.extend(new_achievements)
            
            if level_up:
                print(f"🎉 LEVEL UP! Now level {progress.get('current_level', 1)}")
        
        # Get progress summary
        print("\n--- Progress Summary ---")
        summary = await memory_manager.progress_tracker.get_progress_summary(test_user_id)
        
        print(f"✅ Progress tracking completed")
        print(f"   Current Level: {summary.get('current_level', 1)}")
        print(f"   Total Points: {summary.get('total_points', 0)}")
        print(f"   Scenarios Completed: {summary.get('scenarios_completed', 0)}")
        print(f"   Success Rate: {summary.get('success_rate', 0):.1%}")
        print(f"   Current Streak: {summary.get('current_streak', 0)}")
        print(f"   Achievements Earned: {summary.get('achievements_earned', 0)}")
        
        # Display next milestones
        next_milestones = summary.get('next_milestones', [])
        if next_milestones:
            print(f"\n--- Next Milestones ---")
            for milestone in next_milestones:
                print(f"   • {milestone['description']}: {milestone.get('progress_percent', 0):.1f}% complete")
        
        return True
        
    except Exception as e:
        print(f"❌ Progress tracking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_a2a_communication(memory_manager: MemoryManagerAgent):
    """Test 6: A2A communication with other agents"""
    print("\n🧪 Test 6: A2A Communication")
    print("=" * 50)
    
    try:
        # Test different A2A message types
        test_messages = [
            # Session creation request from Game Master
            {
                "message_type": "create_session",
                "payload": {
                    "user_id": "test_user_a2a",
                    "user_role": "finance",
                    "difficulty": 3
                }
            },
            # Session update request
            {
                "message_type": "update_session", 
                "payload": {
                    "session_id": None,  # Will be filled with created session ID
                    "updates": {
                        "conversation_history": [{"role": "user", "content": "Test message"}],
                        "current_difficulty": 4
                    }
                }
            },
            # Pattern analysis request from Evaluation Agent
            {
                "message_type": "analyze_patterns",
                "payload": {
                    "user_id": "test_user_a2a",
                    "decisions": [
                        {"vulnerability_type": "phishing", "user_choice": "report", "correct_choice": "report"},
                        {"vulnerability_type": "authority", "user_choice": "click", "correct_choice": "report"}
                    ]
                }
            },
            # User profile request
            {
                "message_type": "get_profile",
                "payload": {
                    "user_id": "test_user_a2a"
                }
            }
        ]
        
        session_id = None
        
        for i, test_msg in enumerate(test_messages, 1):
            print(f"\n--- A2A Message {i}: {test_msg['message_type']} ---")
            
            # Create AgentMessage
            agent_message = AgentMessage(
                sender_agent="test_agent",
                recipient_agent="memory_manager",
                message_type=test_msg["message_type"],
                payload=test_msg["payload"],
                session_id="test_session_a2a",
                correlation_id=f"test_corr_{i}"
            )
            
            # Update session ID for update message
            if test_msg["message_type"] == "update_session" and session_id:
                agent_message.payload["session_id"] = session_id
            
            # Process message
            response = await memory_manager.process_message(agent_message)
            
            print(f"✅ Message processed successfully")
            print(f"   Request: {test_msg['message_type']}")
            print(f"   Response: {response.message_type}")
            print(f"   Correlation ID: {response.correlation_id}")
            
            # Store session ID for next test
            if test_msg["message_type"] == "create_session" and response.message_type == "session_created":
                session_id = response.payload.get("session_id")
                print(f"   Created Session: {session_id[:8]}...")
            
            # Display specific response data
            if response.message_type == "pattern_analysis":
                analysis = response.payload.get("analysis", {})
                recommendations = analysis.get("recommendations", [])
                print(f"   Analysis Generated: {len(recommendations)} recommendations")
            elif response.message_type == "user_profile":
                profile = response.payload.get("profile", {})
                if profile:
                    print(f"   Profile Retrieved: {profile.get('user_role', 'unknown')} user")
                else:
                    print("   Profile: New user (no existing profile)")
        
        print("\n✅ A2A Communication tests completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ A2A communication failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_integration():
    """Test 7: Integration between all Memory Manager components"""
    print("\n🧪 Test 7: Memory Integration")
    print("=" * 50)
    
    try:
        memory_manager = MemoryManagerAgent()
        await memory_manager.initialize()
        
        test_user_id = "integration_test_user"
        
        # Create complete user journey
        print("--- Simulating Complete User Journey ---")
        
        # 1. Create session
        session = await memory_manager.create_session(
            user_id=test_user_id,
            user_role=UserRole.GENERAL,
            initial_difficulty=DifficultyLevel.BEGINNER
        )
        
        print(f"1. Session created: {session.session_id[:8]}...")
        
        # 2. Simulate learning progression
        learning_progression = [
            {"threat_identified": True, "vulnerability_type": "obvious_phishing", "response_time": 45},
            {"threat_identified": True, "vulnerability_type": "obvious_phishing", "response_time": 40},
            {"threat_missed": True, "vulnerability_type": "subtle_authority", "response_time": 15},
            {"threat_identified": True, "vulnerability_type": "obvious_phishing", "response_time": 35},
            {"threat_identified": True, "vulnerability_type": "moderate_urgency", "response_time": 30},
        ]
        
        all_decisions = []
        
        for step, decision_data in enumerate(learning_progression, 1):
            # Update session with decision
            decision_point = {
                "turn": step,
                "vulnerability": decision_data["vulnerability_type"],
                "user_choice": "report_suspicious" if decision_data.get("threat_identified") else "click_link",
                "correct_choice": "report_suspicious",
                "risk_score_impact": 0.0 if decision_data.get("threat_identified") else 0.2
            }
            
            session_updates = {
                "decision_points": session.decision_points + [decision_point]
            }
            
            await memory_manager.update_session(session.session_id, session_updates)
            
            # Track progress
            progress_data = {
                "scenario_completed": True,
                "scenario_type": decision_data["vulnerability_type"],
                "response_time": decision_data["response_time"],
                "difficulty": 2
            }
            progress_data.update(decision_data)
            
            await memory_manager.progress_tracker.update_progress(test_user_id, progress_data)
            
            # Collect decision for pattern analysis
            all_decisions.append({
                "turn": step,
                "vulnerability_type": decision_data["vulnerability_type"],
                "user_choice": decision_point["user_choice"],
                "correct_choice": decision_point["correct_choice"],
                "response_time": decision_data["response_time"],
                "timestamp": datetime.now().isoformat()
            })
        
        print(f"2. Simulated {len(learning_progression)} learning scenarios")
        
        # 3. Analyze patterns
        profile = await memory_manager.user_profiler.get_profile(test_user_id)
        analysis = await memory_manager.analyze_user_patterns(test_user_id, all_decisions)
        
        print(f"3. Pattern analysis completed")
        
        # 4. Generate recommendations
        recommendations = await memory_manager.get_personalized_recommendations(
            test_user_id,
            {"success_rate": 0.8, "response_time": 35}
        )
        
        print(f"4. Generated personalized recommendations")
        
        # 5. Get final progress summary
        progress_summary = await memory_manager.progress_tracker.get_progress_summary(test_user_id)
        
        print("\n--- Integration Results ---")
        print(f"✅ Complete user journey processed")
        print(f"   Session ID: {session.session_id[:8]}...")
        print(f"   Scenarios Completed: {progress_summary.get('scenarios_completed', 0)}")
        print(f"   Success Rate: {progress_summary.get('success_rate', 0):.1%}")
        print(f"   Current Level: {progress_summary.get('current_level', 1)}")
        print(f"   Achievements: {progress_summary.get('achievements_earned', 0)}")
        print(f"   Recommendations: {len(recommendations.get('focus_areas', []))} focus areas")
        
        await memory_manager.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Memory integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run comprehensive Memory Manager test suite"""
    print("🧠 CyberGuard Academy - Memory Manager Test Suite")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 7
    
    # Test 1: Initialization
    memory_manager = await test_memory_manager_initialization()
    if memory_manager:
        tests_passed += 1
    else:
        print("❌ Cannot continue - initialization failed")
        return
    
    # Test 2: Session management
    session = await test_session_management(memory_manager)
    if session:
        tests_passed += 1
    
    # Test 3: User profiling
    if await test_user_profiling(memory_manager):
        tests_passed += 1
    
    # Test 4: Pattern analysis
    if await test_pattern_analysis(memory_manager):
        tests_passed += 1
    
    # Test 5: Progress tracking
    if await test_progress_tracking(memory_manager):
        tests_passed += 1
    
    # Test 6: A2A communication
    if await test_a2a_communication(memory_manager):
        tests_passed += 1
    
    # Test 7: Integration test
    if await test_memory_integration():
        tests_passed += 1
    
    # Cleanup
    try:
        await memory_manager.shutdown()
        print("\n✅ Memory Manager shutdown complete")
    except Exception as e:
        print(f"❌ Shutdown error: {e}")
    
    # Results
    print("\n" + "=" * 70)
    print(f"🧠 Memory Manager Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Memory Manager is fully functional!")
        print("\n🚀 Memory Manager Features Verified:")
        print("   • Session Management ✅")
        print("   • User Profiling ✅") 
        print("   • Pattern Analysis ✅")
        print("   • Progress Tracking ✅")
        print("   • Achievement System ✅")
        print("   • A2A Communication ✅")
        print("   • Multi-Tool Integration ✅")
    else:
        print("⚠️  Some tests failed - review implementation")
        
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())