"""
Hint Provider Tool - Adaptive hint system for struggling users.

Provides contextual hints when users are struggling with scenarios:
1. Detects when users need guidance without breaking immersion
2. Provides progressive hints from subtle to explicit  
3. Tracks hint usage for learning analytics
4. Maintains the invisible assessment philosophy
5. Ensures hints feel natural within the narrative

Key principle: Hints should feel like natural guidance, not test answers.
"""

from typing import Dict, Any, Optional, List
import random

from cyberguard.models import CyberGuardSession


class HintProvider:
    """
    Intelligent hint generation for adaptive training support.
    
    Provides contextual guidance when users struggle while maintaining
    immersion and avoiding breaking the training narrative.
    """
    
    def __init__(self):
        self.hint_templates = {}
        self.hint_history = {}
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize hint templates and tracking."""
        print("[HintProvider] Loading hint templates...")
        
        await self._load_hint_templates()
        self.hint_history = {}
        
        self.is_initialized = True
        print("[HintProvider] Hint provider initialized")

    async def shutdown(self) -> None:
        """Clean up resources."""
        print("[HintProvider] Shutting down hint provider")
        self.hint_templates.clear()
        self.hint_history.clear()

    async def generate_hint(
        self,
        user_input: str,
        session_context: CyberGuardSession,
        decision_analysis: Dict[str, Any],
        hint_level: str = "subtle"
    ) -> Optional[str]:
        """
        Generate contextual hint for user.
        
        Args:
            user_input: User's current input
            session_context: Current session state
            decision_analysis: Analysis of user's response
            hint_level: Level of explicitness (subtle, moderate, explicit)
            
        Returns:
            Hint text or None if no hint needed
        """
        if not self.is_initialized:
            await self.initialize()
        
        # Check if user actually needs a hint
        if not self._should_provide_hint(user_input, session_context, decision_analysis):
            return None
        
        # Determine appropriate hint based on context
        vulnerability_type = decision_analysis.get("vulnerability_type", "general")
        user_action = decision_analysis.get("user_action", "unclear")
        
        # Get hint template
        hint_template = self._select_hint_template(
            vulnerability_type=vulnerability_type,
            user_action=user_action,
            hint_level=hint_level,
            session=session_context
        )
        
        if not hint_template:
            return None
        
        # Customize hint for context
        customized_hint = self._customize_hint(
            template=hint_template,
            session_context=session_context,
            decision_analysis=decision_analysis
        )
        
        # Track hint usage
        self._track_hint_usage(
            session_id=session_context.session_id,
            hint_type=vulnerability_type,
            hint_level=hint_level,
            hint_content=customized_hint
        )
        
        print(f"[HintProvider] Providing {hint_level} hint for {vulnerability_type}")
        
        return customized_hint

    def _should_provide_hint(
        self,
        user_input: str,
        session_context: CyberGuardSession,
        decision_analysis: Dict[str, Any]
    ) -> bool:
        """Determine if user needs a hint."""
        
        # Don't provide hints if user is doing well
        if decision_analysis.get("decision_quality") in ["excellent", "good"]:
            return False
        
        # Don't provide too many hints per session
        if session_context.hints_used >= 3:
            return False
        
        # Provide hint if user is struggling
        if decision_analysis.get("user_struggling", False):
            return True
        
        # Provide hint if user made poor decision
        if decision_analysis.get("decision_quality") == "poor":
            return True
        
        # Provide hint if user seems confused
        confusion_indicators = ["confused", "not sure", "help", "don't understand"]
        user_lower = user_input.lower()
        if any(indicator in user_lower for indicator in confusion_indicators):
            return True
        
        return False

    def _select_hint_template(
        self,
        vulnerability_type: str,
        user_action: str,
        hint_level: str,
        session: CyberGuardSession
    ) -> Optional[Dict[str, Any]]:
        """Select appropriate hint template."""
        
        # Get hints for vulnerability type
        vulnerability_hints = self.hint_templates.get(vulnerability_type, {})
        
        # Get hints for action type
        action_hints = vulnerability_hints.get(user_action, vulnerability_hints.get("general", {}))
        
        # Get hints for level
        level_hints = action_hints.get(hint_level, [])
        
        if not level_hints:
            return None
        
        # Select random hint from available options
        return random.choice(level_hints)

    def _customize_hint(
        self,
        template: Dict[str, Any],
        session_context: CyberGuardSession,
        decision_analysis: Dict[str, Any]
    ) -> str:
        """Customize hint template for specific context."""
        
        hint_text = template.get("text", "")
        
        # Replace context variables
        customizations = {
            "{user_role}": session_context.user_role.value,
            "{scenario_type}": session_context.scenario_type.value,
            "{vulnerability}": decision_analysis.get("vulnerability_type", "security issue")
        }
        
        for placeholder, value in customizations.items():
            hint_text = hint_text.replace(placeholder, value)
        
        return hint_text

    async def _load_hint_templates(self) -> None:
        """Load hint templates for different scenarios."""
        
        self.hint_templates = {
            "phishing_email": {
                "click": {
                    "subtle": [
                        {
                            "text": "Before taking any action, you might want to take a closer look at the email details...",
                            "focus": "verification"
                        },
                        {
                            "text": "Consider what information you have about the sender and whether this request is typical...",
                            "focus": "sender_verification"
                        }
                    ],
                    "moderate": [
                        {
                            "text": "This type of urgent request often benefits from verification through known channels before proceeding...",
                            "focus": "independent_verification"
                        },
                        {
                            "text": "When dealing with unexpected requests, it's worth checking if this follows normal company procedures...",
                            "focus": "procedure_check"
                        }
                    ],
                    "explicit": [
                        {
                            "text": "Red flag alert: Unexpected urgent requests for sensitive actions should always be verified independently before clicking any links or providing information.",
                            "focus": "security_warning"
                        }
                    ]
                },
                "unclear": {
                    "subtle": [
                        {
                            "text": "Take a moment to examine the email carefully. What stands out to you about the sender, content, or request?",
                            "focus": "analysis"
                        },
                        {
                            "text": "In situations like this, security professionals often ask: 'Is this request expected and normal?'",
                            "focus": "expectation_check"
                        }
                    ]
                },
                "general": {
                    "subtle": [
                        {
                            "text": "Consider what your organization's security policies would recommend in this situation...",
                            "focus": "policy"
                        },
                        {
                            "text": "Think about how you would verify the authenticity of this type of request...",
                            "focus": "verification"
                        }
                    ]
                }
            },
            "vishing": {
                "general": {
                    "subtle": [
                        {
                            "text": "Unexpected calls requesting sensitive information deserve careful consideration...",
                            "focus": "verification"
                        }
                    ]
                }
            },
            "bec": {
                "general": {
                    "subtle": [
                        {
                            "text": "Executive requests that bypass normal procedures often warrant additional verification...",
                            "focus": "procedure_verification"
                        }
                    ]
                }
            },
            "general": {
                "general": {
                    "subtle": [
                        {
                            "text": "When facing unexpected security situations, consider what verification steps would be appropriate...",
                            "focus": "verification"
                        },
                        {
                            "text": "Think about what additional information would help you make a confident decision...",
                            "focus": "information_gathering"
                        }
                    ]
                }
            }
        }

    def _track_hint_usage(
        self,
        session_id: str,
        hint_type: str,
        hint_level: str,
        hint_content: str
    ) -> None:
        """Track hint usage for analytics."""
        
        if session_id not in self.hint_history:
            self.hint_history[session_id] = []
        
        self.hint_history[session_id].append({
            "hint_type": hint_type,
            "hint_level": hint_level,
            "hint_content": hint_content,
            "timestamp": "current_time"  # Would use actual timestamp
        })

    def get_hint_statistics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get hint usage statistics."""
        
        if session_id:
            return {
                "session_id": session_id,
                "hints_provided": self.hint_history.get(session_id, []),
                "total_hints": len(self.hint_history.get(session_id, []))
            }
        
        total_hints = sum(len(hints) for hints in self.hint_history.values())
        
        return {
            "total_sessions_with_hints": len(self.hint_history),
            "total_hints_provided": total_hints,
            "average_hints_per_session": total_hints / max(len(self.hint_history), 1)
        }