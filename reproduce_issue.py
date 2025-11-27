
import asyncio
import os
from cyberguard.orchestrator import CyberGuardOrchestrator
from cyberguard.models import UserRole, ThreatType

async def reproduce():
    with open("reproduction_log.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")

        log("Initializing Orchestrator...")
        orchestrator = CyberGuardOrchestrator()
        await orchestrator.initialize()

        log("\nCreating Session...")
        session = await orchestrator.create_session(
            user_id="test_user",
            threat_type="phishing",
            user_role="general"
        )
        log(f"Session Created: {session.session_id}")
        log(f"Initial State: {session.current_state}")

        # FORCE STATE TO INTRO TO TEST FIX
        session.current_state = "intro"
        log(f"Forced State: {session.current_state}")

        # Turn 1: User asks "Who is the sender?"
        log("\n--- Turn 1 ---")
        user_input = "Who is the sender?"
        log(f"User Input: {user_input}")
        response = await orchestrator.process_user_action(
            session_id=session.session_id,
            user_message=user_input
        )
        log(f"AI Response: {response.get('narrative')}")
        log(f"State after Turn 1: {session.current_state}")

        # Turn 2: User says "I hover over the sender's address and wait"
        log("\n--- Turn 2 ---")
        user_input = "I hover over the sender's address and wait"
        log(f"User Input: {user_input}")
        response = await orchestrator.process_user_action(
            session_id=session.session_id,
            user_message=user_input
        )
        log(f"AI Response: {response.get('narrative')}")
        log(f"State after Turn 2: {session.current_state}")
        
        # Turn 3: User says "What is the email address of the sender?"
        log("\n--- Turn 3 ---")
        user_input = "What is the email address of the sender?"
        log(f"User Input: {user_input}")
        response = await orchestrator.process_user_action(
            session_id=session.session_id,
            user_message=user_input
        )
        log(f"AI Response: {response.get('narrative')}")
        log(f"State after Turn 3: {session.current_state}")

        await orchestrator.shutdown()

if __name__ == "__main__":
    asyncio.run(reproduce())
