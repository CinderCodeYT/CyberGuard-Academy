"""
Debrief Generator Tool - Creates learning summaries after scenarios.

Generates comprehensive learning debriefs that:
1. Summarize the scenario and user's actions
2. Highlight key learning points without judgment  
3. Provide actionable security recommendations
4. Track improvement areas for future training
5. Maintain positive, growth-focused tone

Key principle: Focus on learning and improvement, never shame or judgment.
"""

from typing import Dict, Any, List
from datetime import datetime

from cyberguard.models import CyberGuardSession, DecisionPoint


class DebriefGenerator:
    """
    Intelligent debrief generation for post-scenario learning.
    
    Creates personalized learning summaries that reinforce security concepts
    while maintaining positive reinforcement and growth mindset.
    """
    
    def __init__(self):
        self.debrief_templates = {}
        self.learning_frameworks = {}
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize debrief templates and learning frameworks."""
        print("[DebriefGenerator] Loading debrief templates...")
        
        await self._load_debrief_templates()
        await self._load_learning_frameworks()
        
        self.is_initialized = True
        print("[DebriefGenerator] Debrief generator initialized")

    async def shutdown(self) -> None:
        """Clean up resources."""
        print("[DebriefGenerator] Shutting down debrief generator")
        self.debrief_templates.clear()
        self.learning_frameworks.clear()

    async def generate_debrief(
        self,
        session: CyberGuardSession,
        completion_reason: str = "natural_completion"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive learning debrief for completed session.
        
        Args:
            session: Completed training session
            completion_reason: How the session ended
            
        Returns:
            Debrief content and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        print(f"[DebriefGenerator] Generating debrief for session {session.session_id}")
        
        # Analyze session performance
        performance_analysis = self._analyze_session_performance(session)
        
        # Generate debrief sections
        debrief_sections = {
            "summary": await self._generate_summary(session, performance_analysis),
            "key_learnings": await self._generate_key_learnings(session, performance_analysis),
            "security_insights": await self._generate_security_insights(session, performance_analysis),
            "recommendations": await self._generate_recommendations(session, performance_analysis),
            "next_steps": await self._generate_next_steps(session, performance_analysis)
        }
        
        # Compile complete debrief
        full_debrief = self._compile_debrief(debrief_sections, performance_analysis)
        
        return {
            "content": full_debrief,
            "sections": debrief_sections,
            "performance_analysis": performance_analysis,
            "completion_reason": completion_reason,
            "generated_at": datetime.utcnow().isoformat(),
            "session_duration": session.calculate_session_duration()
        }

    def _analyze_session_performance(self, session: CyberGuardSession) -> Dict[str, Any]:
        """Analyze session performance and learning outcomes."""
        
        total_decisions = len(session.decision_points)
        correct_decisions = sum(
            1 for decision in session.decision_points
            if decision.risk_score_impact <= 0  # Negative impact is good (reduced risk)
        )
        
        # Calculate performance metrics
        success_rate = correct_decisions / max(total_decisions, 1)
        average_risk_impact = sum(d.risk_score_impact for d in session.decision_points) / max(total_decisions, 1)
        
        # Identify patterns
        vulnerability_patterns = {}
        for decision in session.decision_points:
            vuln_type = decision.vulnerability
            if vuln_type not in vulnerability_patterns:
                vulnerability_patterns[vuln_type] = {"total": 0, "correct": 0}
            vulnerability_patterns[vuln_type]["total"] += 1
            if decision.risk_score_impact <= 0:
                vulnerability_patterns[vuln_type]["correct"] += 1
        
        # Determine overall performance level
        if success_rate >= 0.8:
            performance_level = "excellent"
        elif success_rate >= 0.6:
            performance_level = "good"
        elif success_rate >= 0.4:
            performance_level = "developing"
        else:
            performance_level = "needs_focus"
        
        return {
            "total_decisions": total_decisions,
            "correct_decisions": correct_decisions,
            "success_rate": success_rate,
            "average_risk_impact": average_risk_impact,
            "performance_level": performance_level,
            "vulnerability_patterns": vulnerability_patterns,
            "session_duration": session.calculate_session_duration(),
            "hints_used": session.hints_used,
            "conversation_turns": len(session.conversation_history),
            "scenario_type": session.scenario_type.value,
            "difficulty_level": session.current_difficulty.value
        }

    async def _generate_summary(self, session: CyberGuardSession, analysis: Dict[str, Any]) -> str:
        """Generate session summary section."""
        
        scenario_type = session.scenario_type.value
        performance_level = analysis["performance_level"]
        success_rate = analysis["success_rate"]
        duration_minutes = int(analysis["session_duration"] / 60)
        
        summary_templates = {
            "excellent": f"""
## 🎯 Session Summary

Outstanding work! You navigated this {scenario_type} scenario with strong security awareness, making correct decisions {success_rate:.0%} of the time. Your responses showed excellent instincts for recognizing and handling potential security threats.

**Session Stats:** {duration_minutes} minutes • {analysis['total_decisions']} key decisions • {analysis['hints_used']} hints used
""",
            "good": f"""
## 🎯 Session Summary

Great job! You handled this {scenario_type} scenario well, with correct responses {success_rate:.0%} of the time. Your security awareness is developing nicely, and you showed good judgment in several key areas.

**Session Stats:** {duration_minutes} minutes • {analysis['total_decisions']} key decisions • {analysis['hints_used']} hints used
""",
            "developing": f"""
## 🎯 Session Summary

Good progress! This {scenario_type} scenario provided valuable learning opportunities. You got {success_rate:.0%} of the key decisions right and gained important insights about security practices.

**Session Stats:** {duration_minutes} minutes • {analysis['total_decisions']} key decisions • {analysis['hints_used']} hints used
""",
            "needs_focus": f"""
## 🎯 Session Summary

This {scenario_type} scenario highlighted important learning opportunities. While challenging, each scenario helps build stronger security instincts. The key insights below will help strengthen your approach to similar situations.

**Session Stats:** {duration_minutes} minutes • {analysis['total_decisions']} key decisions • {analysis['hints_used']} hints used
"""
        }
        
        return summary_templates.get(performance_level, summary_templates["developing"])

    async def _generate_key_learnings(self, session: CyberGuardSession, analysis: Dict[str, Any]) -> str:
        """Generate key learnings section."""
        
        learnings = []
        
        # Add scenario-specific learnings
        if session.scenario_type.value == "phishing":
            learnings.extend([
                "🔍 **Email Verification**: Always verify unexpected requests through independent channels",
                "🚩 **Red Flag Recognition**: Urgent language and external senders often indicate phishing attempts",
                "🛡️ **Safe Practices**: When in doubt, verify before clicking or sharing information"
            ])
        
        # Add performance-specific learnings
        if analysis["success_rate"] >= 0.8:
            learnings.append("💡 **Strong Instincts**: Your security awareness is working well - trust those instincts!")
        elif analysis["hints_used"] > 0:
            learnings.append("🤔 **Learning Process**: Taking time to think through security decisions shows good judgment")
        
        # Add vulnerability-specific learnings
        for vuln_type, pattern in analysis["vulnerability_patterns"].items():
            success_rate = pattern["correct"] / pattern["total"]
            if success_rate < 0.5:
                learnings.append(f"📚 **Focus Area**: {vuln_type.replace('_', ' ').title()} - worth additional attention in future training")
        
        learning_text = "\n".join(learnings) if learnings else "💡 Every scenario provides valuable learning opportunities to strengthen security awareness."
        
        return f"""
## 🎓 Key Learnings

{learning_text}
"""

    async def _generate_security_insights(self, session: CyberGuardSession, analysis: Dict[str, Any]) -> str:
        """Generate security insights section."""
        
        insights = []
        
        # Add threat-specific insights
        threat_insights = {
            "phishing": [
                "Phishing attacks often use urgency and authority to bypass careful thinking",
                "Legitimate organizations rarely request sensitive information via unexpected emails",
                "Verification through known channels is your best defense against impersonation"
            ],
            "vishing": [
                "Voice phishing relies on authority and time pressure to manipulate decisions",
                "Real IT departments rarely request credentials over unsolicited calls",
                "Always hang up and call back through official channels to verify requests"
            ],
            "bec": [
                "Business email compromise often targets financial processes and wire transfers",
                "Executive impersonation attacks bypass normal approval processes",
                "Multi-person verification helps prevent unauthorized financial transactions"
            ]
        }
        
        scenario_insights = threat_insights.get(session.scenario_type.value, [
            "Security awareness requires balancing accessibility with protection",
            "When facing uncertainty, verification through known channels provides clarity",
            "Trust your instincts when something feels unusual or unexpected"
        ])
        
        # Add personalized insights based on decisions
        if analysis["average_risk_impact"] > 0.5:
            insights.append("🎯 **Quick Decision Tip**: Taking a moment to pause and verify can prevent most security incidents")
        
        if analysis["hints_used"] == 0 and analysis["success_rate"] >= 0.7:
            insights.append("⭐ **Strong Independence**: You navigated the scenario confidently without needing guidance")
        
        insight_text = "\n".join([f"• {insight}" for insight in scenario_insights[:2] + insights])
        
        return f"""
## 🔐 Security Insights

{insight_text}
"""

    async def _generate_recommendations(self, session: CyberGuardSession, analysis: Dict[str, Any]) -> str:
        """Generate personalized recommendations."""
        
        recommendations = []
        
        # Performance-based recommendations
        if analysis["success_rate"] >= 0.8:
            recommendations.append("Continue building on your strong security instincts with more advanced scenarios")
        elif analysis["success_rate"] >= 0.6:
            recommendations.append("Focus on strengthening verification habits for consistent security decisions")
        else:
            recommendations.append("Practice identifying red flags in low-pressure training environments")
        
        # Vulnerability-specific recommendations
        weak_areas = [
            vuln_type for vuln_type, pattern in analysis["vulnerability_patterns"].items()
            if (pattern["correct"] / pattern["total"]) < 0.5
        ]
        
        if weak_areas:
            focus_area = weak_areas[0].replace("_", " ").title()
            recommendations.append(f"Additional training on {focus_area} scenarios would be beneficial")
        
        # Behavioral recommendations
        if analysis["hints_used"] > 2:
            recommendations.append("Building confidence in security decision-making through regular practice")
        
        rec_text = "\n".join([f"• {rec}" for rec in recommendations[:3]])
        
        return f"""
## 📈 Recommendations

{rec_text}
"""

    async def _generate_next_steps(self, session: CyberGuardSession, analysis: Dict[str, Any]) -> str:
        """Generate next steps for continued learning."""
        
        # Determine appropriate next scenario type
        if analysis["success_rate"] >= 0.8:
            difficulty_suggestion = "Try a more advanced scenario or different threat type"
            next_focus = "expanding your security knowledge across different attack vectors"
        elif analysis["success_rate"] >= 0.6:
            difficulty_suggestion = "Continue with similar difficulty level for consistency"
            next_focus = "building confidence in your security decision-making"
        else:
            difficulty_suggestion = "Practice with similar scenarios to reinforce learning"
            next_focus = "strengthening fundamental security awareness skills"
        
        return f"""
## 🚀 Next Steps

• **Continue Training**: {difficulty_suggestion}
• **Focus Area**: {next_focus}
• **Schedule**: Regular practice helps build security instincts into habits

Your security awareness journey is ongoing - each scenario builds stronger defenses against real threats.
"""

    def _compile_debrief(self, sections: Dict[str, str], analysis: Dict[str, Any]) -> str:
        """Compile all debrief sections into complete document."""
        
        header = f"""
# 🎓 Training Debrief: {analysis['scenario_type'].title()} Scenario

*Completed on {datetime.now().strftime('%B %d, %Y')}*

---
"""
        
        return header + "\n".join(sections.values()) + "\n\n---\n\n*Keep up the great work building your cybersecurity awareness!*"

    async def _load_debrief_templates(self) -> None:
        """Load debrief templates for different scenarios."""
        
        # This would typically load from a database or files
        self.debrief_templates = {
            "phishing": {
                "excellent_summary": "Outstanding phishing recognition skills!",
                "good_summary": "Strong phishing awareness with room for improvement",
                "needs_improvement_summary": "Important learning opportunities identified"
            }
            # Additional templates would be loaded here
        }

    async def _load_learning_frameworks(self) -> None:
        """Load learning frameworks for structured education."""
        
        self.learning_frameworks = {
            "security_decision_framework": [
                "Pause and assess the situation",
                "Identify potential red flags",
                "Verify through independent channels", 
                "Take appropriate protective action",
                "Report if necessary"
            ]
        }