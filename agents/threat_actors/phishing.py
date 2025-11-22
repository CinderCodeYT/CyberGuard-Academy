"""
Phishing Agent - Realistic phishing threat generation for training scenarios.

The Phishing Agent is responsible for:
1. Generating convincing phishing emails with appropriate difficulty levels
2. Adapting scenarios based on user responses and performance
3. Creating safe but realistic threats that challenge users
4. Coordinating with evaluation agent for learning analytics
5. Ensuring all content follows safety guidelines for training

This agent demonstrates real phishing techniques while maintaining
complete safety through controlled redirection and educational focus.
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from cyberguard.agents import ThreatActorAgent
from cyberguard.models import (
    AgentMessage, 
    ScenarioContext, 
    SocialEngineeringPattern, 
    DifficultyLevel, 
    UserRole
)
from cyberguard.config import settings
from tools.email_generator import EmailGenerator
from tools.link_generator import LinkGenerator
from tools.header_spoofing import HeaderSpoofing


class PhishingAgent(ThreatActorAgent):
    """
    Phishing Agent - Creator of realistic phishing scenarios for training.

    This agent creates sophisticated but safe phishing attacks that challenge
    users while providing clear learning opportunities through embedded red flags.
    
    Key Design Principles:
    1. Generate realistic threats that mirror current attack patterns
    2. Adapt complexity based on user skill and performance
    3. Embed educational red flags for post-scenario learning
    4. Ensure complete safety through controlled redirection
    5. Track techniques for evaluation and analytics
    """

    def __init__(self):
        super().__init__("phishing_agent", "phishing")

        # Initialize specialized tools
        self.email_generator = EmailGenerator()
        self.link_generator = LinkGenerator()
        self.header_spoofing = HeaderSpoofing()
        
        # Agent state
        self.active_scenarios = {}
        self.generated_content = {}

    async def initialize(self) -> None:
        """Initialize phishing agent and all specialized tools."""
        print(f"[{self.agent_name}] Initializing Phishing Agent...")
        
        # Initialize all tools
        await self.email_generator.initialize()
        await self.link_generator.initialize()
        await self.header_spoofing.initialize()
        
        print(f"[{self.agent_name}] Phishing Agent initialized successfully")

    async def shutdown(self) -> None:
        """Gracefully shutdown phishing agent and tools."""
        print(f"[{self.agent_name}] Shutting down Phishing Agent...")
        
        # Shutdown tools
        await self.email_generator.shutdown()
        await self.link_generator.shutdown()
        await self.header_spoofing.shutdown()
        
        # Clear state
        self.active_scenarios.clear()
        self.generated_content.clear()
        
        print(f"[{self.agent_name}] Phishing Agent shutdown complete")

    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """
        Process incoming A2A messages from Game Master or other agents.
        
        Handles requests for scenario generation, adaptation, and analytics.
        """
        try:
            print(f"[{self.agent_name}] Processing message: {message.message_type}")
            
            if message.message_type == "generate_scenario":
                return await self._handle_generate_scenario(message)
            elif message.message_type == "adapt_scenario":
                return await self._handle_adapt_scenario(message)
            elif message.message_type == "get_scenario_analytics":
                return await self._handle_get_analytics(message)
            else:
                return self.create_response_message(
                    message,
                    "error",
                    {"error": f"Unknown message type: {message.message_type}"}
                )
                
        except Exception as e:
            print(f"[{self.agent_name}] Error processing message: {str(e)}")
            return self.create_response_message(
                message,
                "error",
                {"error": f"Failed to process message: {str(e)}"}
            )

    async def generate_scenario(self, context: ScenarioContext) -> Dict[str, Any]:
        """
        Generate a phishing scenario based on provided context.
        
        Args:
            context: Scenario generation parameters including user role, 
                    difficulty level, and threat pattern
                    
        Returns:
            Complete phishing scenario with email content, links, and metadata
        """
        print(f"[{self.agent_name}] Generating phishing scenario for {context.user_role.value}")
        
        # Generate phishing email content
        email_content = await self.email_generator.generate_phishing_email(
            threat_pattern=context.threat_pattern,
            user_role=context.user_role,
            difficulty_level=context.difficulty_level,
            session_context={"session_context": context.session_context}
        )
        
        # Generate malicious links within the email
        link_data = await self.link_generator.generate_phishing_link(
            threat_pattern=context.threat_pattern,
            user_role=context.user_role,
            difficulty_level=context.difficulty_level,
            scenario_context={"session_context": context.session_context}
        )
        
        # Generate spoofed email headers
        header_data = await self.header_spoofing.generate_spoofed_headers(
            sender_info=email_content["sender"],
            threat_pattern=context.threat_pattern,
            user_role=context.user_role,
            difficulty_level=context.difficulty_level,
            scenario_context={"session_context": context.session_context}
        )
        
        # Integrate link into email body
        email_body_with_link = self._integrate_link_into_email(
            email_content["body"],
            link_data["display_url"]
        )
        
        # Combine all components into complete scenario
        scenario = {
            "scenario_id": str(uuid.uuid4()),
            "email": {
                "headers": header_data["headers"],
                "sender": email_content["sender"],
                "subject": email_content["subject"],
                "body": email_body_with_link,
                "attachments": email_content["attachments"]
            },
            "link": {
                "display_url": link_data["display_url"],
                "actual_url": link_data["actual_url"],
                "parameters": link_data["parameters"]
            },
            "red_flags": {
                "email_flags": email_content["red_flags"],
                "link_flags": link_data["red_flags"], 
                "header_flags": header_data["red_flags"]
            },
            "metadata": {
                "threat_pattern": context.threat_pattern.value,
                "difficulty_level": context.difficulty_level.value,
                "target_role": context.user_role.value,
                "educational_objectives": self._get_educational_objectives(
                    email_content, link_data, header_data
                ),
                "generated_at": datetime.utcnow().isoformat()
            }
        }
        
        # Store scenario for potential adaptation
        self.active_scenarios[scenario["scenario_id"]] = scenario
        
        print(f"[{self.agent_name}] Generated scenario: {scenario['scenario_id']}")
        return scenario

    async def adapt_scenario(
        self, 
        session_id: str, 
        user_response: str, 
        performance_hint: str
    ) -> Dict[str, Any]:
        """
        Adapt ongoing scenario based on user responses and performance.
        
        Args:
            session_id: Current session identifier
            user_response: Latest user input or action
            performance_hint: Guidance on difficulty adjustment
            
        Returns:
            Adapted scenario content or follow-up communications
        """
        print(f"[{self.agent_name}] Adapting scenario based on user response")
        
        # Analyze user response
        response_analysis = self._analyze_user_response(user_response)
        
        # Determine adaptation strategy
        adaptation_strategy = self._determine_adaptation_strategy(
            response_analysis, 
            performance_hint
        )
        
        # Generate adapted content
        adapted_content = await self._generate_adapted_content(
            adaptation_strategy,
            user_response,
            session_id
        )
        
        return {
            "adaptation_type": adaptation_strategy,
            "content": adapted_content,
            "reasoning": f"Adapted based on {response_analysis} and {performance_hint}",
            "session_id": session_id
        }

    # Message handlers for A2A communication
    async def _handle_generate_scenario(self, message: AgentMessage) -> AgentMessage:
        """Handle scenario generation requests from Game Master."""
        
        payload = message.payload
        
        # Extract context from message
        context = ScenarioContext(
            user_role=UserRole(payload.get("user_role", "general")),
            difficulty_level=DifficultyLevel(payload.get("difficulty", 2)),
            threat_pattern=SocialEngineeringPattern(
                payload.get("threat_pattern", SocialEngineeringPattern.URGENCY.value)
            ),
            session_context=payload.get("user_context", "")
        )
        
        # Generate scenario
        scenario = await self.generate_scenario(context)
        
        return self.create_response_message(
            message,
            "scenario_ready",
            {"scenario_content": scenario}
        )

    async def _handle_adapt_scenario(self, message: AgentMessage) -> AgentMessage:
        """Handle scenario adaptation requests."""
        
        payload = message.payload
        
        # Adapt scenario based on user feedback
        adaptation = await self.adapt_scenario(
            session_id=payload.get("session_id", ""),
            user_response=payload.get("user_response", ""),
            performance_hint=payload.get("performance_hint", "maintain_difficulty")
        )
        
        return self.create_response_message(
            message,
            "scenario_adapted",
            {"adaptation": adaptation}
        )

    async def _handle_get_analytics(self, message: AgentMessage) -> AgentMessage:
        """Handle requests for scenario analytics."""
        
        analytics = {
            "active_scenarios": len(self.active_scenarios),
            "generated_content_count": len(self.generated_content),
            "techniques_used": self._get_techniques_summary()
        }
        
        return self.create_response_message(
            message,
            "analytics_data",
            {"analytics": analytics}
        )

    # Helper methods
    def _integrate_link_into_email(self, email_body: str, phishing_link: str) -> str:
        """Integrate the phishing link into the email body naturally."""
        
        # Replace placeholder links with actual phishing links
        link_replacements = {
            "[VERIFY ACCOUNT NOW]": f'<a href="{phishing_link}">VERIFY ACCOUNT NOW</a>',
            "[AUTHORIZE PAYMENT]": f'<a href="{phishing_link}">AUTHORIZE PAYMENT</a>',
            "[UPDATE PASSWORD]": f'<a href="{phishing_link}">UPDATE PASSWORD</a>',
            "[CLAIM BONUS]": f'<a href="{phishing_link}">CLAIM BONUS</a>'
        }
        
        modified_body = email_body
        for placeholder, replacement in link_replacements.items():
            modified_body = modified_body.replace(placeholder, replacement)
        
        return modified_body

    def _get_educational_objectives(
        self, 
        email_content: Dict[str, Any], 
        link_data: Dict[str, Any], 
        header_data: Dict[str, Any]
    ) -> List[str]:
        """Extract educational objectives from generated content."""
        
        objectives = []
        
        # Email-based objectives
        if email_content.get("red_flags"):
            for flag in email_content["red_flags"]:
                if flag["type"] == "credential_request":
                    objectives.append("recognize_credential_theft_attempts")
                elif flag["type"] == "urgent_action_request":
                    objectives.append("identify_artificial_urgency")
        
        # Link-based objectives  
        if link_data.get("red_flags"):
            for flag in link_data["red_flags"]:
                if flag["type"] == "suspicious_domain":
                    objectives.append("verify_link_domains")
        
        # Header-based objectives
        if header_data.get("red_flags"):
            for flag in header_data["red_flags"]:
                if flag["type"] == "sender_mismatch":
                    objectives.append("check_sender_consistency")
        
        return list(set(objectives))  # Remove duplicates

    def _analyze_user_response(self, user_response: str) -> str:
        """Analyze user response to determine their understanding level."""
        
        response_lower = user_response.lower()
        
        if any(word in response_lower for word in ["suspicious", "fake", "phishing", "don't trust"]):
            return "user_identified_threat"
        elif any(word in response_lower for word in ["click", "verify", "login", "update"]):
            return "user_falling_for_threat"
        elif any(word in response_lower for word in ["check", "verify", "investigate", "unsure"]):
            return "user_investigating"
        else:
            return "user_response_unclear"

    def _determine_adaptation_strategy(self, response_analysis: str, performance_hint: str) -> str:
        """Determine how to adapt the scenario based on user performance."""
        
        if response_analysis == "user_identified_threat":
            if "increase_difficulty" in performance_hint:
                return "escalate_threat"
            else:
                return "provide_confirmation"
        elif response_analysis == "user_falling_for_threat":
            if "decrease_difficulty" in performance_hint:
                return "add_obvious_red_flags"
            else:
                return "provide_subtle_warning"
        elif response_analysis == "user_investigating":
            return "provide_investigative_clues"
        else:
            return "provide_clarification"

    async def _generate_adapted_content(
        self, 
        strategy: str, 
        user_response: str, 
        session_id: str
    ) -> Dict[str, Any]:
        """Generate adapted content based on strategy."""
        
        if strategy == "escalate_threat":
            return {
                "type": "follow_up_email",
                "content": "You received a follow-up message: 'We notice you haven't verified yet. Your account will be permanently deleted in 30 minutes.'",
                "red_flags_added": ["extreme_urgency", "deletion_threat"]
            }
        elif strategy == "provide_confirmation":
            return {
                "type": "positive_feedback",
                "content": "Good instincts! You correctly identified this as a phishing attempt.",
                "learning_points": ["Always verify sender", "Check for urgency pressure"]
            }
        elif strategy == "add_obvious_red_flags":
            return {
                "type": "modified_email",
                "content": "The email now shows obvious spelling errors: 'Pleas verify you're acount immediatly'",
                "red_flags_added": ["spelling_errors", "grammar_mistakes"]
            }
        else:
            return {
                "type": "guidance",
                "content": "Take a closer look at the sender's email address and the urgency of the request.",
                "hints": ["Check domain carefully", "Question urgent requests"]
            }

    def _get_techniques_summary(self) -> Dict[str, int]:
        """Get summary of techniques used across all scenarios."""
        
        techniques_count = {}
        
        for scenario in self.active_scenarios.values():
            threat_pattern = scenario["metadata"]["threat_pattern"]
            techniques_count[threat_pattern] = techniques_count.get(threat_pattern, 0) + 1
        
        return techniques_count