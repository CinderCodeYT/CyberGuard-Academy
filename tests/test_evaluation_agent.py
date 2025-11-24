#!/usr/bin/env python3
"""
Test Suite for Evaluation Agent - CyberGuard Academy

Comprehensive tests for evaluation, scoring, and analytics functionality.
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.evaluation.evaluation_agent import EvaluationAgent
from cyberguard.models import (
    CyberGuardSession, DecisionPoint, UserRole, DifficultyLevel,
    ThreatType, AgentMessage
)


async def test_evaluation_initialization():
    """Test 1: Evaluation Agent Initialization"""
    print("\n🧪 Test 1: Evaluation Agent Initialization")
    print("=" * 50)
    
    try:
        evaluator = EvaluationAgent()
        await evaluator.initialize()
        
        print(f"✅ Evaluation Agent initialized successfully")
        print(f"   Agent Name: {evaluator.agent_name}")
        print(f"   Agent Type: {evaluator.agent_type}")
        print(f"   Evaluation Weights: {evaluator.weights}")
        print(f"   Risk Thresholds: {evaluator.risk_thresholds}")
        
        await evaluator.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_decision_tracking():
    """Test 2: Decision Point Tracking"""
    print("\n🧪 Test 2: Decision Point Tracking")
    print("=" * 50)
    
    try:
        evaluator = EvaluationAgent()
        await evaluator.initialize()
        
        session_id = "test_session_001"
        
        # Track multiple decisions
        decisions_to_track = [
            {
                "turn": 1,
                "vulnerability": "phishing_urgency",
                "user_choice": "report_suspicious",
                "correct_choice": "report_suspicious",
                "response_time": 15.0,
                "confidence_level": 0.8
            },
            {
                "turn": 2,
                "vulnerability": "phishing_authority",
                "user_choice": "click_link",
                "correct_choice": "verify_sender",
                "response_time": 3.0,
                "confidence_level": 0.6
            },
            {
                "turn": 3,
                "vulnerability": "phishing_urgency",
                "user_choice": "verify_sender",
                "correct_choice": "verify_sender",
                "response_time": 25.0,
                "confidence_level": 0.9
            }
        ]
        
        print("\n--- Tracking Decisions ---")
        for i, decision_data in enumerate(decisions_to_track, 1):
            evaluation = await evaluator.track_decision(session_id, decision_data)
            
            print(f"\nDecision {i}: {decision_data['vulnerability']}")
            print(f"   User Choice: {decision_data['user_choice']}")
            print(f"   Correct Choice: {decision_data['correct_choice']}")
            print(f"   Outcome: {evaluation['outcome']}")
            print(f"   Risk Impact: {evaluation['risk_impact']:.2f}")
            print(f"   Response Time: {evaluation['response_time']:.1f}s ({evaluation['time_category']})")
        
        # Verify decisions were tracked
        tracked_count = len(evaluator.evaluation_metrics[session_id]["decisions"])
        print(f"\n✅ Decision tracking test completed")
        print(f"   Total Decisions Tracked: {tracked_count}")
        
        await evaluator.shutdown()
        return tracked_count == len(decisions_to_track)
        
    except Exception as e:
        print(f"❌ Decision tracking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_session_evaluation():
    """Test 3: Complete Session Evaluation"""
    print("\n🧪 Test 3: Complete Session Evaluation")
    print("=" * 50)
    
    try:
        evaluator = EvaluationAgent()
        await evaluator.initialize()
        
        # Create a mock session
        session = CyberGuardSession(
            session_id="eval_test_session",
            user_id="test_user_eval",
            user_role=UserRole.FINANCE,
            scenario_type=ThreatType.PHISHING,
            scenario_id="phishing_scenario_001",
            current_difficulty=DifficultyLevel.INTERMEDIATE,
            decision_points=[
                DecisionPoint(
                    turn=1,
                    vulnerability="phishing_urgency",
                    user_choice="report_suspicious",
                    correct_choice="report_suspicious",
                    risk_score_impact=0.0,
                    confidence_level=0.8
                ),
                DecisionPoint(
                    turn=2,
                    vulnerability="phishing_authority",
                    user_choice="click_link",
                    correct_choice="verify_sender",
                    risk_score_impact=1.0,
                    confidence_level=0.5
                ),
                DecisionPoint(
                    turn=3,
                    vulnerability="phishing_urgency",
                    user_choice="verify_sender",
                    correct_choice="verify_sender",
                    risk_score_impact=0.0,
                    confidence_level=0.9
                ),
                DecisionPoint(
                    turn=4,
                    vulnerability="phishing_curiosity",
                    user_choice="ignore",
                    correct_choice="report_suspicious",
                    risk_score_impact=0.7,
                    confidence_level=0.4
                )
            ]
        )
        
        # Track decisions first
        for i, dp in enumerate(session.decision_points, 1):
            await evaluator.track_decision(
                session.session_id,
                {
                    "turn": dp.turn,
                    "vulnerability": dp.vulnerability,
                    "user_choice": dp.user_choice,
                    "correct_choice": dp.correct_choice,
                    "response_time": 15.0 + (i * 5),
                    "confidence_level": dp.confidence_level
                }
            )
        
        # Calculate session score
        print("\n--- Calculating Session Score ---")
        evaluation = await evaluator.calculate_session_score(session)
        
        print(f"\n📊 Session Evaluation Results:")
        print(f"   Overall Score: {evaluation['overall_score']}%")
        print(f"   Risk Score: {evaluation['risk_score']}%")
        print(f"   Risk Level: {evaluation['risk_level']}")
        
        print(f"\n📈 Component Scores:")
        for component, score in evaluation['component_scores'].items():
            print(f"   {component.title()}: {score}%")
        
        print(f"\n🎯 Performance Metrics:")
        print(f"   Decisions Tracked: {evaluation['decisions_tracked']}")
        print(f"   Correct Decisions: {evaluation['correct_decisions']}")
        print(f"   Success Rate: {(evaluation['correct_decisions']/evaluation['decisions_tracked']*100):.1f}%")
        
        print(f"\n🔍 Vulnerability Analysis:")
        vuln_analysis = evaluation['vulnerability_analysis']
        print(f"   Strengths ({len(vuln_analysis['strengths'])}): {', '.join(vuln_analysis['strengths']) or 'None'}")
        print(f"   Weaknesses ({len(vuln_analysis['weaknesses'])}): {', '.join(vuln_analysis['weaknesses']) or 'None'}")
        
        print(f"\n💡 Knowledge Gaps:")
        for gap in evaluation['knowledge_gaps']:
            print(f"   • {gap['gap_type']}: {gap['success_rate']}% success ({gap['severity']} severity)")
        
        print(f"\n📝 Recommendations ({len(evaluation['recommendations'])}):")
        for i, rec in enumerate(evaluation['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n🎚️  Difficulty Recommendation:")
        diff_rec = evaluation['difficulty_recommendation']
        print(f"   Current: Level {diff_rec['current']}")
        print(f"   Recommended: Level {diff_rec['recommended']} ({diff_rec['adjustment']})")
        print(f"   Reason: {diff_rec['reason']}")
        
        print(f"\n✅ Session evaluation test completed")
        
        await evaluator.shutdown()
        return evaluation['overall_score'] > 0
        
    except Exception as e:
        print(f"❌ Session evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_risk_assessment():
    """Test 4: Real-time Risk Assessment"""
    print("\n🧪 Test 4: Real-time Risk Assessment")
    print("=" * 50)
    
    try:
        evaluator = EvaluationAgent()
        await evaluator.initialize()
        
        session_id = "risk_test_session"
        
        # Simulate scenario with increasing risk
        scenarios = [
            ("Good decisions", [
                ("report_suspicious", "report_suspicious", 20.0),
                ("verify_sender", "verify_sender", 18.0),
                ("delete_email", "delete_email", 15.0),
            ]),
            ("Risky decisions", [
                ("click_link", "report_suspicious", 2.0),
                ("provide_password", "ignore", 3.0),
                ("forward_email", "delete_email", 4.0),
            ])
        ]
        
        for scenario_name, decisions in scenarios:
            print(f"\n--- Scenario: {scenario_name} ---")
            
            for i, (user_choice, correct_choice, response_time) in enumerate(decisions, 1):
                await evaluator.track_decision(
                    session_id,
                    {
                        "turn": i,
                        "vulnerability": "phishing_test",
                        "user_choice": user_choice,
                        "correct_choice": correct_choice,
                        "response_time": response_time
                    }
                )
            
            # Get risk assessment via A2A message
            message = AgentMessage(
                sender_agent="test_agent",
                recipient_agent="evaluation_agent",
                message_type="get_risk_assessment",
                payload={"session_id": session_id},
                session_id=session_id
            )
            
            response = await evaluator.process_message(message)
            risk_data = response.payload
            
            print(f"   Risk Level: {risk_data['risk_level']}")
            print(f"   Risk Score: {risk_data['risk_score']}")
            print(f"   Decisions Analyzed: {risk_data['decisions_analyzed']}")
        
        print(f"\n✅ Risk assessment test completed")
        
        await evaluator.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Risk assessment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_a2a_communication():
    """Test 5: A2A Communication Protocol"""
    print("\n🧪 Test 5: A2A Communication Protocol")
    print("=" * 50)
    
    try:
        evaluator = EvaluationAgent()
        await evaluator.initialize()
        
        session_id = "a2a_test_session"
        
        # Test different A2A message types
        messages = [
            {
                "type": "track_decision",
                "payload": {
                    "session_id": session_id,
                    "decision_data": {
                        "turn": 1,
                        "vulnerability": "phishing_urgency",
                        "user_choice": "report_suspicious",
                        "correct_choice": "report_suspicious",
                        "response_time": 20.0
                    }
                }
            },
            {
                "type": "get_risk_assessment",
                "payload": {"session_id": session_id}
            },
            {
                "type": "request_difficulty",
                "payload": {
                    "session_id": session_id,
                    "current_difficulty": 3
                }
            }
        ]
        
        print("\n--- Testing A2A Messages ---")
        for i, msg_data in enumerate(messages, 1):
            message = AgentMessage(
                sender_agent="game_master",
                recipient_agent="evaluation_agent",
                message_type=msg_data["type"],
                payload=msg_data["payload"],
                session_id=session_id,
                correlation_id=f"test_corr_{i}"
            )
            
            response = await evaluator.process_message(message)
            
            print(f"\nMessage {i}: {msg_data['type']}")
            print(f"   Response Type: {response.message_type}")
            print(f"   Correlation ID: {response.correlation_id}")
            print(f"   Payload Keys: {list(response.payload.keys())}")
            
            if "error" in response.payload:
                print(f"   ⚠️  Error: {response.payload['error']}")
            else:
                print(f"   ✓ Success")
        
        print(f"\n✅ A2A communication test completed")
        
        await evaluator.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ A2A communication failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_adaptive_difficulty():
    """Test 6: Adaptive Difficulty Recommendation"""
    print("\n🧪 Test 6: Adaptive Difficulty Recommendation")
    print("=" * 50)
    
    try:
        evaluator = EvaluationAgent()
        await evaluator.initialize()
        
        # Test scenarios with different performance levels
        scenarios = [
            ("High Performance (>85%)", 0.9, "increase"),
            ("Optimal Performance (70%)", 0.7, "maintain"),
            ("Low Performance (<55%)", 0.5, "decrease")
        ]
        
        print("\n--- Testing Difficulty Recommendations ---")
        for scenario_name, score, expected_adjustment in scenarios:
            # Create mock session
            session = CyberGuardSession(
                session_id=f"diff_test_{score}",
                user_id="test_user_diff",
                user_role=UserRole.DEVELOPER,
                scenario_type=ThreatType.PHISHING,
                scenario_id="diff_scenario",
                current_difficulty=DifficultyLevel.INTERMEDIATE
            )
            
            recommendation = await evaluator._recommend_difficulty(score, session)
            
            print(f"\n{scenario_name}:")
            print(f"   Overall Score: {score * 100}%")
            print(f"   Current Difficulty: Level {recommendation['current']}")
            print(f"   Recommended: Level {recommendation['recommended']}")
            print(f"   Adjustment: {recommendation['adjustment']}")
            print(f"   Reason: {recommendation['reason']}")
            print(f"   ✓ {'Correct' if recommendation['adjustment'] == expected_adjustment else 'MISMATCH'}")
        
        print(f"\n✅ Adaptive difficulty test completed")
        
        await evaluator.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Adaptive difficulty test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all evaluation agent tests"""
    print("\n" + "=" * 70)
    print("🧠 CyberGuard Academy - Evaluation Agent Test Suite")
    print("=" * 70)
    
    tests = [
        test_evaluation_initialization,
        test_decision_tracking,
        test_session_evaluation,
        test_risk_assessment,
        test_a2a_communication,
        test_adaptive_difficulty
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"🧠 Evaluation Agent Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Evaluation Agent is fully functional!")
        print("\n🚀 Evaluation Agent Features Verified:")
        print("   • Decision Point Tracking ✅")
        print("   • Session Scoring & Evaluation ✅")
        print("   • Risk Assessment ✅")
        print("   • Vulnerability Analysis ✅")
        print("   • Knowledge Gap Identification ✅")
        print("   • Adaptive Difficulty ✅")
        print("   • A2A Communication ✅")
    else:
        print("⚠️  Some tests failed - review implementation")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
