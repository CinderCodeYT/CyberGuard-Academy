"""
Quick test script to verify the session state and message duplication fixes.
"""
import asyncio
import json
import requests
import time

API_BASE = "http://localhost:8000"

def test_scenario_flow():
    """Test that state transitions work and messages don't duplicate."""
    print("\n🧪 Testing Session State and Message Handling...")
    
    # 1. Create a new session
    print("\n1️⃣ Creating new session...")
    response = requests.post(
        f"{API_BASE}/sessions/create",
        json={
            "user_id": "test_fix_user",
            "threat_type": "phishing",
            "difficulty": 2,
            "user_role": "general"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        print(response.text)
        return
    
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"✅ Session created: {session_id}")
    print(f"   Initial state: {session_data.get('current_state')}")
    print(f"   Initial messages: {len(session_data.get('conversation_history', []))}")
    
    # 2. Send first user response (should transition to scenario_active)
    print("\n2️⃣ Sending first user message (should trigger phishing email)...")
    time.sleep(1)  # Give it a moment
    
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/action",
        json={
            "action_type": "message",
            "user_message": "Yes, I'm ready to begin training"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        print(response.text)
        return
    
    action_data = response.json()
    print(f"✅ Response received")
    print(f"   Narrative length: {len(action_data.get('narrative', ''))}")
    
    # 3. Get session state to verify transition
    print("\n3️⃣ Checking session state after first message...")
    response = requests.get(f"{API_BASE}/sessions/{session_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get session: {response.status_code}")
        return
    
    session_data = response.json()
    current_state = session_data.get("current_state")
    conversation = session_data.get("conversation_history", [])
    
    print(f"   Current state: {current_state}")
    print(f"   Total messages: {len(conversation)}")
    
    # Check for duplicates
    user_messages = [msg for msg in conversation if msg["role"] == "user"]
    gm_messages = [msg for msg in conversation if msg["role"] == "game_master"]
    
    print(f"   User messages: {len(user_messages)}")
    print(f"   GM messages: {len(gm_messages)}")
    
    # Look for duplicate content
    user_contents = [msg["content"] for msg in user_messages]
    if len(user_contents) != len(set(user_contents)):
        print("   ❌ DUPLICATE USER MESSAGES DETECTED!")
        for i, content in enumerate(user_contents):
            print(f"      {i}: {content[:50]}...")
    else:
        print("   ✅ No duplicate user messages")
    
    # Verify state transition
    if current_state == "scenario_active":
        print("   ✅ State correctly transitioned to scenario_active")
    else:
        print(f"   ❌ State is {current_state}, expected scenario_active")
    
    # 4. Send second message (should get contextual response, not new email)
    print("\n4️⃣ Sending second message (should get contextual response)...")
    time.sleep(1)
    
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/action",
        json={
            "action_type": "message",
            "user_message": "I want to verify this email by calling IT"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to send second message: {response.status_code}")
        return
    
    action_data = response.json()
    narrative = action_data.get("narrative", "")
    print(f"✅ Response received")
    print(f"   Response preview: {narrative[:150]}...")
    
    # Check if it's generating a NEW email (bad) or responding contextually (good)
    if "From:" in narrative and "Subject:" in narrative:
        print("   ⚠️  Response looks like a NEW email (should be contextual!)")
    else:
        print("   ✅ Response appears contextual")
    
    # 5. Check final session state
    print("\n5️⃣ Final session check...")
    response = requests.get(f"{API_BASE}/sessions/{session_id}")
    session_data = response.json()
    
    conversation = session_data.get("conversation_history", [])
    decision_points = session_data.get("decision_points", [])
    
    print(f"   Total messages: {len(conversation)}")
    print(f"   Decision points recorded: {len(decision_points)}")
    
    if decision_points:
        last_decision = decision_points[-1]
        print(f"   Last decision:")
        print(f"      User choice: {last_decision.get('user_choice')}")
        print(f"      Correct choice: {last_decision.get('correct_choice')}")
        print(f"      Risk impact: {last_decision.get('risk_score_impact')}")
        
        if last_decision.get('correct_choice') and last_decision.get('risk_score_impact') != 0.0:
            print("   ✅ Decision tracking working correctly")
        else:
            print("   ⚠️  Decision tracking has empty/zero values")
    
    # Save session file for inspection
    print(f"\n💾 Session saved to: data/sessions/{session_id}.json")
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        test_scenario_flow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
