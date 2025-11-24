"""
CyberGuard Academy - Streamlit UI

Interactive web interface for cybersecurity training scenarios.
Provides a chat-based interface with scenario selection, real-time interaction,
and comprehensive evaluation feedback.
"""

import streamlit as st
import requests
from datetime import datetime
from typing import Dict, Any, Optional
import time

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="CyberGuard Academy",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Helper Functions
# ============================================================================

def create_session(user_id: str, threat_type: str, difficulty: int, user_role: str) -> Optional[Dict[str, Any]]:
    """Create a new training session via API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/sessions",
            json={
                "user_id": user_id,
                "threat_type": threat_type,
                "difficulty": difficulty,
                "user_role": user_role
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to create session: {e}")
        return None


def send_user_action(session_id: str, user_message: str, action_type: str = "message") -> Optional[Dict[str, Any]]:
    """Send user action to API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/sessions/action",
            json={
                "session_id": session_id,
                "user_message": user_message,
                "action_type": action_type
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to process action: {e}")
        return None


def complete_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Complete session and get evaluation."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/sessions/{session_id}/complete",
            params={"reason": "user_completion"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to complete session: {e}")
        return None


def check_api_health() -> bool:
    """Check if API is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# ============================================================================
# Session State Initialization
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "scenario_active" not in st.session_state:
    st.session_state.scenario_active = False
if "evaluation_data" not in st.session_state:
    st.session_state.evaluation_data = None
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# ============================================================================
# Main UI
# ============================================================================

# Header
st.title("🛡️ CyberGuard Academy")
st.markdown("**Interactive Cybersecurity Training with Invisible Assessment**")

# Check API health
if not check_api_health():
    st.error("⚠️ API server is not responding. Please start the API server first:")
    st.code("python api.py", language="bash")
    st.stop()

# ============================================================================
# Sidebar - Configuration Panel
# ============================================================================

with st.sidebar:
    st.header("⚙️ Training Configuration")
    
    # User ID (can be customized)
    user_id = st.text_input(
        "User ID",
        value=st.session_state.user_id,
        help="Anonymized user identifier for progress tracking"
    )
    st.session_state.user_id = user_id
    
    st.divider()
    
    # Scenario Selection
    st.subheader("Scenario Settings")
    
    threat_type = st.selectbox(
        "Threat Type",
        options=["phishing", "vishing", "bec", "physical", "insider"],
        help="Type of cybersecurity threat to practice"
    )
    
    difficulty = st.slider(
        "Difficulty Level",
        min_value=1,
        max_value=5,
        value=3,
        help="1 = Beginner, 5 = Expert"
    )
    
    user_role = st.selectbox(
        "Your Role",
        options=["general", "developer", "manager", "executive", "hr", "finance", "it_admin"],
        help="Your job function for personalized scenarios"
    )
    
    st.divider()
    
    # Start/Reset buttons
    col1, col2 = st.columns(2)
    
    with col1:
        start_button = st.button(
            "🎯 Start Training",
            disabled=st.session_state.scenario_active,
            use_container_width=True
        )
    
    with col2:
        reset_button = st.button(
            "🔄 Reset",
            disabled=not st.session_state.scenario_active,
            use_container_width=True
        )
    
    # Handle Start button
    if start_button:
        with st.spinner("Initializing scenario..."):
            session_data = create_session(
                user_id=user_id,
                threat_type=threat_type,
                difficulty=difficulty,
                user_role=user_role
            )
            
            if session_data:
                st.session_state.session_id = session_data["session_id"]
                st.session_state.scenario_active = True
                st.session_state.conversation_history = [
                    {"role": "game_master", "content": session_data["opening_narrative"]}
                ]
                st.session_state.evaluation_data = None
                st.success("✅ Scenario started!")
                st.rerun()
    
    # Handle Reset button
    if reset_button:
        if st.session_state.session_id:
            # Complete the session before reset
            complete_session(st.session_state.session_id)
        
        st.session_state.session_id = None
        st.session_state.conversation_history = []
        st.session_state.scenario_active = False
        st.session_state.evaluation_data = None
        st.success("✅ Reset complete!")
        st.rerun()
    
    st.divider()
    
    # Status display
    st.subheader("📊 Status")
    if st.session_state.scenario_active:
        st.success("🟢 Scenario Active")
        st.info(f"**Session:** `{st.session_state.session_id[:8]}...`")
    else:
        st.warning("🔴 No Active Scenario")


# ============================================================================
# Main Content Area
# ============================================================================

# Chat Interface
st.header("💬 Training Scenario")

# Display conversation history
chat_container = st.container()
with chat_container:
    for message in st.session_state.conversation_history:
        role = message["role"]
        content = message["content"]
        
        if role == "game_master":
            with st.chat_message("assistant", avatar="🎮"):
                st.markdown(content)
        elif role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)

# User input (only if scenario is active)
if st.session_state.scenario_active and not st.session_state.evaluation_data:
    user_input = st.chat_input("Your response...", key="user_input")
    
    if user_input:
        # Add user message to history
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Send to API
        with st.spinner("Processing..."):
            response = send_user_action(
                session_id=st.session_state.session_id,
                user_message=user_input,
                action_type="message"
            )
        
        if response:
            # Add Game Master response
            st.session_state.conversation_history.append({
                "role": "game_master",
                "content": response["narrative"]
            })
            
            # Check if scenario is complete
            if response.get("scenario_complete", False):
                st.session_state.evaluation_data = response.get("debrief")
                st.balloons()
            
            st.rerun()

# Action buttons (only if scenario is active)
if st.session_state.scenario_active and not st.session_state.evaluation_data:
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚨 Report Phishing", use_container_width=True):
            with st.spinner("Reporting..."):
                response = send_user_action(
                    session_id=st.session_state.session_id,
                    user_message="I want to report this as phishing",
                    action_type="report_phishing"
                )
                if response:
                    st.session_state.conversation_history.append({
                        "role": "game_master",
                        "content": response["narrative"]
                    })
                    if response.get("scenario_complete", False):
                        st.session_state.evaluation_data = response.get("debrief")
                    st.rerun()
    
    with col2:
        if st.button("🔗 Click Link", use_container_width=True):
            with st.spinner("Processing..."):
                response = send_user_action(
                    session_id=st.session_state.session_id,
                    user_message="I clicked on the link in the message",
                    action_type="click_link"
                )
                if response:
                    st.session_state.conversation_history.append({
                        "role": "game_master",
                        "content": response["narrative"]
                    })
                    if response.get("scenario_complete", False):
                        st.session_state.evaluation_data = response.get("debrief")
                    st.rerun()
    
    with col3:
        if st.button("❓ Request Hint", use_container_width=True):
            with st.spinner("Generating hint..."):
                response = send_user_action(
                    session_id=st.session_state.session_id,
                    user_message="I need a hint",
                    action_type="request_hint"
                )
                if response:
                    st.session_state.conversation_history.append({
                        "role": "game_master",
                        "content": response["narrative"]
                    })
                    st.rerun()
    
    with col4:
        if st.button("✅ Complete Scenario", use_container_width=True):
            with st.spinner("Completing scenario..."):
                evaluation = complete_session(st.session_state.session_id)
                if evaluation:
                    st.session_state.evaluation_data = evaluation
                    st.rerun()


# ============================================================================
# Evaluation & Debrief Section
# ============================================================================

if st.session_state.evaluation_data:
    st.divider()
    st.header("📊 Your Results & Learning Debrief")
    
    eval_data = st.session_state.evaluation_data
    
    # Score Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = eval_data.get("overall_score", 0)
        st.metric("Overall Score", f"{score:.1f}/100", help="Your performance score")
    
    with col2:
        risk_level = eval_data.get("risk_level", "unknown")
        risk_color = {
            "low": "🟢",
            "moderate": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }.get(risk_level.lower(), "⚪")
        st.metric("Risk Level", f"{risk_color} {risk_level.title()}")
    
    with col3:
        duration = eval_data.get("duration_seconds", 0)
        st.metric("Duration", f"{duration:.1f}s")
    
    # Component Scores
    st.subheader("📈 Component Scores")
    component_scores = eval_data.get("component_scores", {})
    
    if component_scores:
        cols = st.columns(len(component_scores))
        for idx, (component, score) in enumerate(component_scores.items()):
            with cols[idx]:
                st.metric(
                    component.replace("_", " ").title(),
                    f"{score:.1f}",
                    help=f"Performance in {component.replace('_', ' ')}"
                )
    
    # Vulnerability Analysis
    st.subheader("🔍 Vulnerability Analysis")
    vulnerabilities = eval_data.get("vulnerability_analysis", [])
    
    if vulnerabilities:
        for vuln in vulnerabilities:
            with st.expander(f"⚠️ {vuln.get('pattern', 'Unknown Pattern')}"):
                st.write(f"**Severity:** {vuln.get('severity', 'N/A')}")
                st.write(f"**Description:** {vuln.get('description', 'No description available')}")
                st.write(f"**Recommendation:** {vuln.get('recommendation', 'No recommendation available')}")
    else:
        st.info("No specific vulnerabilities identified. Great job!")
    
    # Recommendations
    st.subheader("💡 Recommendations for Improvement")
    recommendations = eval_data.get("recommendations", [])
    
    if recommendations:
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.success("Excellent performance! Keep up the good work!")
    
    # Detailed feedback table
    if "detailed_feedback" in eval_data:
        st.subheader("📋 Detailed Feedback")
        st.table(eval_data["detailed_feedback"])


# ============================================================================
# Footer
# ============================================================================

st.divider()
st.caption("🛡️ CyberGuard Academy - Multi-Agent Cybersecurity Training Platform | Powered by Google ADK & Gemini")
