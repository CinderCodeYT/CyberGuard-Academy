"""
Narrative Manager Tool - Generates contextual dialogue and maintains immersion.

This tool handles all narrative generation for the Game Master:
1. Opening scenario introductions
2. Adaptive responses to user actions  
3. Learning moments and educational content
4. Maintaining conversational flow and immersion
5. Incorporating threat content from specialized agents

Key principle: Never break immersion by revealing the training nature.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import random

from cyberguard.models import CyberGuardSession, UserRole, ThreatType
from cyberguard.config import settings
from cyberguard.gemini_client import GeminiClient


class NarrativeManager:
    """
    Intelligent narrative generation for immersive cybersecurity training.
    
    Maintains conversational flow while seamlessly incorporating threats,
    providing learning moments, and adapting to user responses.
    """
    
    def __init__(self):
        self.narrative_templates = {}
        self.response_patterns = {}
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize narrative templates and response patterns."""
        print("[NarrativeManager] Loading narrative templates...")
        
        await self._load_narrative_templates()
        await self._load_response_patterns()
        
        self.is_initialized = True
        print("[NarrativeManager] Narrative manager initialized")

    async def shutdown(self) -> None:
        """Clean up resources."""
        print("[NarrativeManager] Shutting down narrative manager")
        self.narrative_templates.clear()
        self.response_patterns.clear()

    async def generate_opening(
        self,
        scenario_details: Dict[str, Any],
        user_context: Any
    ) -> str:
        """Generate engaging opening narrative for scenario using Gemini AI."""
        
        scenario_type = scenario_details.get("id", "generic")
        user_role = user_context.user_role if hasattr(user_context, 'user_role') else UserRole.GENERAL
        
        system_instruction = """You are a training facilitator for corporate security awareness education.

**CONTEXT**: You help employees practice recognizing security threats in a safe training environment.

Your role: Create realistic workplace scenarios for security awareness training.

GUIDELINES:
1. Write naturally as if describing a normal workday
2. Don't mention "training", "test", or "scenario" 
3. Keep it conversational and brief (2-3 paragraphs)
4. Set up the situation naturally

Goal: Create an engaging training exercise opening."""
        
        prompt = f"""Generate an opening narrative for a cybersecurity training scenario.

User Role: {user_role.value}
Scenario Type: {scenario_type}
Scenario Description: {scenario_details.get('description', 'A typical workday')}
Current Time: {self._get_time_context()}

Create a brief, immersive opening (2-3 paragraphs) that:
1. Establishes the user's role and current work context
2. Sets a natural tone for the scenario to unfold
3. Makes the user feel engaged and present in the moment
4. Does NOT reveal this is training or mention any "scenario"

Write in second person ("You arrive at...") to increase immersion."""
        
        try:
            # Use Gemini Pro for complex narrative generation
            narrative = await GeminiClient.generate_text(
                prompt=prompt,
                model_type="pro",
                temperature=0.8,  # Higher creativity for engaging narratives
                max_tokens=512,
                system_instruction=system_instruction
            )
            
            return narrative.strip()
            
        except Exception as e:
            print(f"[NarrativeManager] Gemini generation failed: {e}, using template")
            # Fallback to template
            return self._generate_opening_fallback(scenario_type, user_role, scenario_details)

    async def generate_threat_presentation(
        self,
        threat_content: Dict[str, Any],
        user_context: str,
        session: CyberGuardSession
    ) -> str:
        """Generate narrative that naturally presents the threat using Gemini AI."""
        
        threat_type = session.scenario_type
        
        system_instruction = """You are the Game Master presenting a security threat within an immersive training scenario.

CRITICAL RULES:
1. Present the threat NATURALLY as if it's a real workplace event
2. NEVER break immersion or reveal this is training
3. Include the actual threat content (email, phone call, etc.) in a natural way
4. Keep the presentation concise and conversational
5. Don't explain or point out red flags - let the user discover them

Present the threat as something that just happened in their workday."""
        
        if threat_type == ThreatType.PHISHING:
            prompt = self._build_phishing_presentation_prompt(threat_content, user_context, session)
        elif threat_type == ThreatType.VISHING:
            prompt = self._build_vishing_presentation_prompt(threat_content, user_context, session)
        elif threat_type == ThreatType.BEC:
            prompt = self._build_bec_presentation_prompt(threat_content, user_context, session)
        else:
            prompt = self._build_generic_presentation_prompt(threat_content, user_context, session)
        
        try:
            # Use Gemini Pro for narrative presentation
            narrative = await GeminiClient.generate_text(
                prompt=prompt,
                model_type="pro",
                temperature=0.7,
                max_tokens=512,
                system_instruction=system_instruction
            )
            
            return narrative.strip()
            
        except Exception as e:
            print(f"[NarrativeManager] Gemini generation failed: {e}, using template")
            # Fallback to template-based presentation
            if threat_type == ThreatType.PHISHING:
                return self._present_phishing_threat(threat_content, user_context, session)
            elif threat_type == ThreatType.VISHING:
                return self._present_vishing_threat(threat_content, user_context, session)
            elif threat_type == ThreatType.BEC:
                return self._present_bec_threat(threat_content, user_context, session)
            else:
                return self._present_generic_threat(threat_content, user_context, session)

    async def analyze_user_response(
        self,
        user_input: str,
        session_context: CyberGuardSession,
        current_scenario_state: str
    ) -> Dict[str, Any]:
        """Analyze user response for decision points and next actions."""
        
        analysis = {
            "is_decision_point": False,
            "is_security_decision": False,
            "user_action": "unclear",
            "decision_quality": "neutral",
            "vulnerability_type": "none",
            "optimal_action": "none",
            "risk_impact": 0.0,
            "user_struggling": False,
            "scenario_resolved": False
        }
        
        user_lower = user_input.lower()
        
        # Detect security-related keywords and actions
        security_actions = {
            "verify": ["verify", "check", "confirm", "validate", "call", "contact", "ask", "inquire", "sender"],
            "report": ["report", "forward", "escalate", "notify", "alert", "flag"],
            "ignore": ["ignore", "delete", "discard", "skip", "trash"],
            "click": ["click", "open", "download", "access", "view", "link"],
            "respond": ["reply", "respond", "answer", "send", "email back"]
        }
        
        detected_action = "unclear"
        for action, keywords in security_actions.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_action = action
                break
        
        analysis["user_action"] = detected_action
        analysis["is_decision_point"] = detected_action != "unclear"
        analysis["is_security_decision"] = detected_action in ["verify", "report", "ignore", "click"]
        
        # Determine decision quality and risk based on scenario context
        if session_context.scenario_type == ThreatType.PHISHING:
            analysis.update(self._analyze_phishing_response(detected_action, user_input))
        
        # Check if user is struggling (asking for help, expressing confusion)
        struggle_indicators = ["help", "confused", "not sure", "don't know", "unclear"]
        analysis["user_struggling"] = any(indicator in user_lower for indicator in struggle_indicators)
        
        # Check if scenario should end
        resolution_indicators = ["done", "finished", "complete", "end"]
        analysis["scenario_resolved"] = any(indicator in user_lower for indicator in resolution_indicators)
        
        return analysis

    def _analyze_phishing_response(self, action: str, full_input: str) -> Dict[str, Any]:
        """Analyze user response to phishing scenario."""
        
        results = {
            "vulnerability_type": "phishing_email",
            "optimal_action": "verify_sender_then_report",
            "risk_impact": 0.0,
            "decision_quality": "neutral"
        }
        
        if action == "click":
            results.update({
                "decision_quality": "poor",
                "risk_impact": 0.8,
                "explanation": "Clicking suspicious links without verification creates high risk"
            })
        elif action == "verify":
            results.update({
                "decision_quality": "excellent", 
                "risk_impact": -0.3,
                "explanation": "Verification is the optimal security practice"
            })
        elif action == "report":
            results.update({
                "decision_quality": "good",
                "risk_impact": -0.2, 
                "explanation": "Reporting suspicious content helps protect others"
            })
        elif action == "ignore":
            results.update({
                "decision_quality": "acceptable",
                "risk_impact": 0.1,
                "explanation": "Ignoring is safe but doesn't help prevent future attacks"
            })
        
        return results

    async def generate_adaptive_response(
        self,
        user_action: str,
        session_context: CyberGuardSession,
        decision_quality: str
    ) -> str:
        """Generate contextual response based on user action using Gemini AI."""
        
        system_instruction = """You are the Game Master responding to a user's action in a cybersecurity training scenario.

CRITICAL RULES:
1. Maintain complete immersion - never break character or reveal training
2. Respond naturally to what the user just did
3. Be encouraging but honest about security implications
4. Keep responses brief (1-2 paragraphs)
5. Don't lecture - guide through natural conversation
6. Use appropriate tone based on decision quality

Your goal: Acknowledge their action and naturally guide the scenario forward."""
        
        # Build conversation context (last 6 turns to include threat presentation)
        conversation_context = ""
        if session_context.conversation_history:
            recent_history = session_context.conversation_history[-6:]
            conversation_context = "Recent conversation:\n"
            for msg in recent_history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                # Limit each message to 300 chars to avoid token bloat
                conversation_context += f"{role.upper()}: {content[:300]}\n"
        
        prompt = f"""The user just took this action: {user_action}
Decision quality: {decision_quality}
Scenario type: {session_context.scenario_type.value if session_context.scenario_type else 'unknown'}
Current phase: {session_context.current_phase}

{conversation_context}

Generate a brief, natural response that:
1. Acknowledges what they just did
2. Reflects the quality of their decision (excellent/good/poor/acceptable)
3. Moves the scenario forward naturally (e.g., if they asked to "check sender", show the sender info)
4. Stays in character as their immersive work environment

Keep it conversational and brief (1-2 short paragraphs)."""
        
        print(f"[NarrativeManager DEBUG] Generating adaptive response for action: {user_action}")
        print(f"[NarrativeManager DEBUG] Decision quality: {decision_quality}")
        print(f"[NarrativeManager DEBUG] Prompt: {prompt[:200]}...")
        
        try:
            response = await GeminiClient.generate_text(
                prompt=prompt,
                model_type="flash",  # Use Flash for quick responses
                temperature=0.6,
                max_tokens=256,
                system_instruction=system_instruction
            )
            
            print(f"[NarrativeManager DEBUG] AI response: {response[:100]}...")
            
            return response.strip()
            
        except Exception as e:
            print(f"[NarrativeManager] Gemini generation failed: {e}, using template")
            # Fallback to template responses
            return self._generate_adaptive_response_fallback(decision_quality)

    async def generate_learning_moment(
        self,
        user_decision: str,
        optimal_action: str, 
        vulnerability_type: str,
        session_context: CyberGuardSession
    ) -> str:
        """Generate educational content after user decision."""
        
        learning_templates = {
            "phishing_email": {
                "excellent": """
Great job! You handled that phishing attempt perfectly. Here's what made it suspicious:

🚩 **Red Flags You Caught:**
• External email address despite claiming to be internal
• Urgent language designed to bypass careful thinking
• Request for sensitive information or immediate action

💡 **Your Response:** Verifying the sender before taking action is exactly the right approach. This prevents most phishing attacks from succeeding.

**Key Takeaway:** When in doubt, verify independently through known channels.
""",
                "poor": """
This was actually a phishing attempt! Here's what happened:

🚩 **Red Flags in This Message:**
• The sender's email domain didn't match the claimed organization
• Urgent language designed to create time pressure
• Request for immediate action without proper verification

⚠️ **The Risk:** Clicking that link would have led to a credential harvesting site designed to steal login information.

💡 **Better Approach:** Always verify suspicious requests through independent channels before taking action.

**Remember:** Real organizations rarely request urgent actions via unexpected emails.
"""
            }
        }
        
        quality_key = "excellent" if user_decision == optimal_action else "poor"
        
        template = learning_templates.get(vulnerability_type, {}).get(quality_key)
        
        if template:
            return template
        else:
            return f"""
**Learning Moment**

Your response: {user_decision}
Optimal approach: {optimal_action}

This scenario highlighted important security considerations. The key is always balancing accessibility with security, and when in doubt, verify through known channels.
"""

    def _present_phishing_threat(
        self,
        threat_content: Dict[str, Any],
        user_context: str,
        session: CyberGuardSession
    ) -> str:
        """Present phishing threat naturally within narrative."""
        
        email_subject = threat_content.get("subject", "Important Message")
        email_body = threat_content.get("body", "Please review the attached information.")
        
        return f"""
As you settle in to work, you notice a new email in your inbox that seems urgent:

**From:** IT-Security@company-alerts.net
**To:** You
**Subject:** {email_subject}

"{email_body}"

The email includes a prominent button labeled "Verify Account Now" and mentions that your account will be suspended if you don't respond within 24 hours.

What would you like to do?
"""

    def _present_vishing_threat(self, threat_content: Dict[str, Any], user_context: str, session: CyberGuardSession) -> str:
        """Present vishing (voice phishing) threat."""
        return "Your phone rings with a call from someone claiming to be from IT support..."

    def _present_bec_threat(self, threat_content: Dict[str, Any], user_context: str, session: CyberGuardSession) -> str:
        """Present business email compromise threat."""
        return "You receive what appears to be an urgent message from a senior executive..."

    def _present_generic_threat(self, threat_content: Dict[str, Any], user_context: str, session: CyberGuardSession) -> str:
        """Present generic threat scenario."""
        return "A potential security situation has emerged that requires your attention..."

    async def generate_fallback_scenario(self, scenario_type: ThreatType, user_context: str) -> str:
        """Generate basic scenario when specialized agents unavailable."""
        
        fallback_scenarios = {
            ThreatType.PHISHING: """
You're reviewing your email when you notice a message from what appears to be your bank, asking you to verify your account information due to "suspicious activity." 

The email looks legitimate but something feels off about the urgency and the request.

How would you handle this situation?
""",
            ThreatType.VISHING: """
You receive a phone call from someone claiming to be from your IT department. They say there's been a security breach and they need you to provide your login credentials to "secure your account."

The caller seems to know some details about your company but the request feels unusual.

What would you do?
""",
            ThreatType.BEC: """
You receive an email that appears to be from your CEO asking you to urgently process a confidential wire transfer to a new vendor. The email emphasizes secrecy and immediate action.

While the email address looks correct, the request is outside normal procedures.

How would you respond?
"""
        }
        
        return fallback_scenarios.get(scenario_type, "A security situation has emerged that requires your attention...")

    async def generate_clarification(self, user_input: str, session_context: CyberGuardSession) -> str:
        """Generate clarifying response when user needs more information."""
        
        clarifications = [
            "To help you think through this situation, consider what verification steps you might take...",
            "Take a moment to consider what red flags, if any, you notice in this scenario...",
            "Think about your organization's normal procedures for this type of request...",
            "What additional information would help you make a confident security decision here?"
        ]
        
        return random.choice(clarifications)
    
    # ===== GEMINI HELPER METHODS =====
    
    def _generate_opening_fallback(
        self,
        scenario_type: str,
        user_role: UserRole,
        scenario_details: Dict[str, Any]
    ) -> str:
        """Fallback template-based opening when Gemini fails."""
        opening_template = self._select_opening_template(scenario_type, user_role)
        
        narrative = opening_template.format(
            role_context=self._get_role_context(user_role),
            scenario_context=scenario_details.get("description", ""),
            time_context=self._get_time_context()
        )
        
        return narrative
    
    def _build_phishing_presentation_prompt(
        self,
        threat_content: Dict[str, Any],
        user_context: str,
        session: CyberGuardSession
    ) -> str:
        """Build prompt for presenting phishing email threat."""
        
        email = threat_content
        
        prompt = f"""Present a phishing email that just arrived in the user's inbox.

Context: The user is at their desk checking emails during a normal workday.

Email Details:
- From: {email.get('sender', {}).get('display_name', 'Unknown')}
- Subject: {email.get('subject', 'Important Message')}
- Body: {email.get('body', 'Email content')}

Present this naturally, as if narrating what they see. Include:
1. Brief context (e.g., "As you're checking your morning emails...")
2. The email sender, subject, and full body content
3. A natural prompt for what they want to do

Format the email clearly but naturally. Keep the whole presentation under 200 words."""
        
        return prompt
    
    def _build_vishing_presentation_prompt(
        self,
        threat_content: Dict[str, Any],
        user_context: str,
        session: CyberGuardSession
    ) -> str:
        """Build prompt for presenting vishing (phone call) threat."""
        
        prompt = f"""Present a vishing (voice phishing) scenario where the user receives a suspicious phone call.

Context: {user_context}

Call Details: {threat_content.get('description', 'Suspicious call from someone claiming to be IT support')}

Present this as a natural phone call interruption during their workday. Include:
1. When/how the call comes in
2. What the caller says and claims
3. What they're requesting
4. A natural prompt for the user's response

Keep it conversational and under 150 words."""
        
        return prompt
    
    def _build_bec_presentation_prompt(
        self,
        threat_content: Dict[str, Any],
        user_context: str,
        session: CyberGuardSession
    ) -> str:
        """Build prompt for presenting business email compromise threat."""
        
        prompt = f"""Present a business email compromise (BEC) scenario where the user receives a suspicious message from a senior executive.

Context: {user_context}

Message Details: {threat_content.get('description', 'Urgent request from executive')}

Present this as an urgent message that just came through. Include:
1. The context of receiving the message
2. Who it appears to be from and their position
3. What they're requesting
4. The urgency/pressure in the request
5. A natural prompt for the user's response

Keep it under 200 words."""
        
        return prompt
    
    def _build_generic_presentation_prompt(
        self,
        threat_content: Dict[str, Any],
        user_context: str,
        session: CyberGuardSession
    ) -> str:
        """Build prompt for presenting generic security threat."""
        
        prompt = f"""Present a security situation that just emerged.

Context: {user_context}
Threat Details: {threat_content.get('description', 'A security situation requiring attention')}

Present this naturally as something that just happened in their workday. Include:
1. What they notice or receive
2. Key details of the security situation
3. A natural prompt for their response

Keep it under 150 words."""
        
        return prompt
    
    def _generate_adaptive_response_fallback(self, decision_quality: str) -> str:
        """Fallback template responses when Gemini fails."""
        
        if decision_quality == "excellent":
            return random.choice([
                "Excellent instincts! You took exactly the right approach by verifying first.",
                "Perfect response! That's exactly what security-aware professionals do.",
                "Outstanding! Your verification step shows strong security awareness."
            ])
        elif decision_quality == "good":
            return random.choice([
                "Good thinking! That's a solid security practice.",
                "Nice work! You're demonstrating good security awareness.",
                "Well done! That response shows you're thinking about security."
            ])
        elif decision_quality == "poor":
            return random.choice([
                "That action would have significant security implications. Let's explore what happened...",
                "Interesting choice. This situation had some important security considerations...",
                "That's a common reaction, but there were some red flags to consider..."
            ])
        else:
            return random.choice([
                "Let me help clarify the situation...",
                "There are a few things to consider here...",
                "This is a good opportunity to think through the security aspects..."
            ])


    async def generate_general_response(self, user_input: str, session_context: CyberGuardSession) -> str:
        """Generate general conversational response."""
        
        responses = [
            "I understand. Let's continue with the scenario...",
            "That's a thoughtful observation. What would you like to do next?",
            "Good question. How would you approach this situation?",
            "Let's think through the security implications here..."
        ]
        
        return random.choice(responses)

    async def _load_narrative_templates(self) -> None:
        """Load narrative templates for different scenarios."""
        
        self.narrative_templates = {
            "opening_general": """
It's {time_context} and you're {role_context}. 

{scenario_context}

You're focused on your work when something draws your attention...
""",
            "opening_developer": """
It's {time_context} and you're working on a critical deployment when {scenario_context}

The development team is pushing to meet today's release deadline...
""",
            "opening_finance": """
It's {time_context} in the finance department. You're reviewing quarterly reports when {scenario_context}

End-of-quarter deadlines are approaching fast...
"""
        }

    async def _load_response_patterns(self) -> None:
        """Load response patterns for different user actions."""
        
        self.response_patterns = {
            "verification_positive": [
                "Smart approach! Verification is always the right first step.",
                "Excellent instinct! That's exactly what security-conscious professionals do.",
                "Perfect! Taking time to verify shows strong security awareness."
            ],
            "immediate_action": [
                "That's a common reaction, but let's consider the security implications...",
                "Interesting choice. There were some important details to consider...",
                "That action would have consequences. Let's explore what happened..."
            ]
        }

    def _select_opening_template(self, scenario_type: str, user_role: UserRole) -> str:
        """Select appropriate opening narrative template."""
        
        role_specific_key = f"opening_{user_role.value}"
        if role_specific_key in self.narrative_templates:
            return self.narrative_templates[role_specific_key]
        else:
            return self.narrative_templates["opening_general"]

    def _get_role_context(self, user_role: UserRole) -> str:
        """Get role-specific context for narrative."""
        
        contexts = {
            UserRole.DEVELOPER: "working on code reviews and deployment tasks",
            UserRole.FINANCE: "managing financial reports and vendor payments", 
            UserRole.EXECUTIVE: "handling strategic decisions and team coordination",
            UserRole.HR: "processing employee onboarding and personnel matters",
            UserRole.GENERAL: "handling your daily responsibilities"
        }
        
        return contexts.get(user_role, contexts[UserRole.GENERAL])

    def _get_time_context(self) -> str:
        """Get appropriate time context for narrative."""
        
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 12:
            return "a busy Tuesday morning"
        elif 12 <= current_hour < 17:
            return "Tuesday afternoon"
        elif 17 <= current_hour < 21:
            return "Tuesday evening"
        else:
            return "late Tuesday night"