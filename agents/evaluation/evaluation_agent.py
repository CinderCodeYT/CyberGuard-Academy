#!/usr/bin/env python3
"""
Evaluation Agent - CyberGuard Academy

Provides invisible assessment and learning analytics for training scenarios.
Tracks user decisions, calculates risk scores, identifies knowledge gaps,
and generates performance insights without disrupting the user experience.

Key Responsibilities:
- Track decision points during scenarios (invisible to user)
- Calculate risk scores and vulnerability metrics
- Identify knowledge gaps and learning patterns
- Generate post-scenario evaluations and recommendations
- Communicate with Game Master and Memory Manager via A2A protocol
- Provide adaptive difficulty recommendations

Evaluation Dimensions:
1. Recognition: Did user identify the threat?
2. Response Time: How quickly did they react?
3. Action Quality: What action did they take?
4. Confidence Level: How certain were they?
5. Pattern Recognition: Can they identify recurring patterns?
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from loguru import logger

from cyberguard.agents import BaseAgent
from cyberguard.models import (
    AgentMessage, CyberGuardSession, DecisionPoint,
    DifficultyLevel, SocialEngineeringPattern, ThreatType
)
from cyberguard.config import Settings


class EvaluationAgent(BaseAgent):
    """
    Evaluation Agent for CyberGuard Academy.
    
    Performs invisible assessment of user security awareness and decision-making.
    Provides analytics and recommendations without disrupting training immersion.
    
    The agent operates in the background, tracking user behavior patterns and
    generating insights that inform adaptive difficulty and personalized learning paths.
    """
    
    def __init__(self, agent_name: str = "evaluation_agent"):
        """Initialize the Evaluation Agent."""
        super().__init__(agent_name, "evaluator")
        self.config = Settings()
        
        # Evaluation criteria weights (configurable)
        self.weights = {
            "recognition": 0.40,      # Did they identify the threat?
            "response_time": 0.20,    # How quickly did they respond?
            "action_quality": 0.30,   # Quality of their action
            "confidence": 0.10        # How confident were they?
        }
        
        # Risk scoring parameters
        self.risk_thresholds = {
            "critical": 0.8,  # 80%+ risk score
            "high": 0.6,      # 60-80% risk score
            "medium": 0.4,    # 40-60% risk score
            "low": 0.2        # 20-40% risk score
        }
        
        # Response time thresholds (seconds)
        self.time_thresholds = {
            "hasty": 5,      # < 5s (too quick, not thinking)
            "optimal": 30,   # 5-30s (good thinking time)
            "slow": 60       # 30-60s (deliberate)
        }
        
        logger.info(f"[{self.agent_name}] Evaluation Agent created")
    
    async def initialize(self) -> None:
        """Initialize agent resources and connections."""
        logger.info(f"[{self.agent_name}] Initializing Evaluation Agent...")
        
        # Load evaluation models and criteria
        await self._load_evaluation_criteria()
        
        # Initialize metrics tracking
        self.evaluation_metrics: Dict[str, Any] = {}
        
        logger.info(f"[{self.agent_name}] Evaluation Agent initialized successfully")
    
    async def shutdown(self) -> None:
        """Clean up agent resources."""
        logger.info(f"[{self.agent_name}] Shutting down Evaluation Agent...")
        
        # Persist any pending evaluations
        await self._persist_pending_evaluations()
        
        logger.info(f"[{self.agent_name}] Evaluation Agent shutdown complete")
    
    # ==================== Core Evaluation Methods ====================
    
    async def track_decision(
        self,
        session_id: str,
        decision_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track a user decision point for evaluation.
        
        This is the primary method for recording user decisions during scenarios.
        Called by the Game Master when the user makes a significant choice.
        
        Args:
            session_id: Session where decision was made
            decision_data: Decision details including:
                - turn: Conversation turn number
                - vulnerability: Type being tested (e.g., "phishing_urgency")
                - user_choice: What the user chose
                - correct_choice: Optimal security action
                - response_time: Time taken to decide (seconds)
                - confidence_level: User's confidence (0.0-1.0, optional)
                
        Returns:
            Decision evaluation with immediate feedback
        """
        logger.debug(f"[{self.agent_name}] Tracking decision for session: {session_id[:8]}...")
        
        try:
            # Create structured decision point
            decision_point = DecisionPoint(
                turn=decision_data.get("turn", 0),
                vulnerability=decision_data.get("vulnerability", "unknown"),
                user_choice=decision_data.get("user_choice", ""),
                correct_choice=decision_data.get("correct_choice", ""),
                risk_score_impact=0.0,  # Will be calculated
                timestamp=decision_data.get("timestamp", datetime.now(timezone.utc).timestamp()),
                confidence_level=decision_data.get("confidence_level")
            )
            
            # Calculate risk score impact
            evaluation = await self._evaluate_decision(decision_point, decision_data)
            decision_point.risk_score_impact = evaluation["risk_impact"]
            
            # Store in session-level tracking
            if session_id not in self.evaluation_metrics:
                self.evaluation_metrics[session_id] = {
                    "decisions": [],
                    "patterns": {},
                    "started_at": datetime.now(timezone.utc)
                }
            
            self.evaluation_metrics[session_id]["decisions"].append({
                "decision_point": decision_point.dict(),
                "evaluation": evaluation
            })
            
            logger.info(
                f"[{self.agent_name}] Decision tracked: "
                f"{decision_point.vulnerability} -> {evaluation['outcome']}"
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Failed to track decision: {e}")
            return {"error": str(e), "outcome": "error"}
    
    async def calculate_session_score(
        self,
        session: CyberGuardSession
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive evaluation for a completed session.
        
        Generates detailed analytics including:
        - Overall risk score
        - Performance by vulnerability type
        - Learning insights and recommendations
        - Adaptive difficulty suggestions
        
        Args:
            session: Completed training session
            
        Returns:
            Comprehensive evaluation results
        """
        logger.info(f"[{self.agent_name}] Calculating session score: {session.session_id[:8]}...")
        
        try:
            # Retrieve tracked decisions
            session_metrics = self.evaluation_metrics.get(session.session_id, {})
            decisions = session_metrics.get("decisions", [])
            
            if not decisions:
                logger.warning(f"[{self.agent_name}] No decisions tracked for session")
                return self._generate_empty_evaluation()
            
            # Calculate component scores
            recognition_score = await self._calculate_recognition_score(decisions)
            response_time_score = await self._calculate_response_time_score(decisions)
            action_quality_score = await self._calculate_action_quality_score(decisions)
            confidence_score = await self._calculate_confidence_score(decisions)
            
            # Calculate weighted overall score
            overall_score = (
                recognition_score * self.weights["recognition"] +
                response_time_score * self.weights["response_time"] +
                action_quality_score * self.weights["action_quality"] +
                confidence_score * self.weights["confidence"]
            )
            
            # Calculate risk score (inverse of performance)
            risk_score = 1.0 - overall_score
            
            # Analyze patterns and gaps
            vulnerability_analysis = await self._analyze_vulnerability_patterns(decisions)
            knowledge_gaps = await self._identify_knowledge_gaps(decisions, vulnerability_analysis)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                risk_score,
                vulnerability_analysis,
                knowledge_gaps
            )
            
            # Suggest adaptive difficulty adjustment
            difficulty_recommendation = await self._recommend_difficulty(overall_score, session)
            
            evaluation = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "scenario_type": session.scenario_type.value,
                "overall_score": round(overall_score * 100, 1),  # Convert to percentage
                "risk_score": round(risk_score * 100, 1),
                "risk_level": self._categorize_risk(risk_score),
                "component_scores": {
                    "recognition": round(recognition_score * 100, 1),
                    "response_time": round(response_time_score * 100, 1),
                    "action_quality": round(action_quality_score * 100, 1),
                    "confidence": round(confidence_score * 100, 1)
                },
                "decisions_tracked": len(decisions),
                "correct_decisions": sum(1 for d in decisions if d["evaluation"]["outcome"] == "correct"),
                "vulnerability_analysis": vulnerability_analysis,
                "knowledge_gaps": knowledge_gaps,
                "recommendations": recommendations,
                "difficulty_recommendation": difficulty_recommendation,
                "session_duration": session.calculate_session_duration(),
                "evaluated_at": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(
                f"[{self.agent_name}] Session evaluation complete: "
                f"Score={evaluation['overall_score']}%, Risk={evaluation['risk_level']}"
            )
            
            return evaluation
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Failed to calculate session score: {e}")
            return {"error": str(e)}
    
    # ==================== A2A Communication ====================
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """
        Process incoming A2A messages from other agents.
        
        Supported message types:
        - track_decision: Record a user decision point
        - evaluate_session: Calculate session score
        - get_risk_assessment: Get current risk level
        - request_difficulty: Get difficulty recommendation
        """
        logger.info(f"[{self.agent_name}] Processing message: {message.message_type}")
        
        try:
            if message.message_type == "track_decision":
                response_payload = await self._handle_track_decision(message.payload)
                response_type = "decision_tracked"
                
            elif message.message_type == "evaluate_session":
                response_payload = await self._handle_evaluate_session(message.payload)
                response_type = "evaluation_complete"
                
            elif message.message_type == "get_risk_assessment":
                response_payload = await self._handle_risk_assessment(message.payload)
                response_type = "risk_assessment"
                
            elif message.message_type == "request_difficulty":
                response_payload = await self._handle_difficulty_request(message.payload)
                response_type = "difficulty_recommendation"

            elif message.message_type == "session_started":
                # Just acknowledge, maybe reset internal state for this session if needed
                response_payload = {"status": "acknowledged"}
                response_type = "session_started_ack"

            elif message.message_type == "decision_made":
                # Map decision_made to track_decision logic
                response_payload = await self._handle_track_decision(message.payload)
                response_type = "decision_tracked"

            elif message.message_type == "get_evaluation":
                # Map get_evaluation to evaluate_session logic
                response_payload = await self._handle_evaluate_session(message.payload)
                response_type = "evaluation_data"
                
            else:
                logger.warning(f"[{self.agent_name}] Unknown message type: {message.message_type}")
                response_payload = {"error": f"Unknown message type: {message.message_type}"}
                response_type = "error"
            
            return AgentMessage(
                sender_agent=self.agent_name,
                recipient_agent=message.sender_agent,
                message_type=response_type,
                payload=response_payload,
                session_id=message.session_id,
                correlation_id=message.correlation_id
            )
            
        except Exception as e:
            logger.error(f"[{self.agent_name}] Error processing message: {e}")
            return AgentMessage(
                sender_agent=self.agent_name,
                recipient_agent=message.sender_agent,
                message_type="error",
                payload={"error": str(e)},
                session_id=message.session_id,
                correlation_id=message.correlation_id
            )
    
    # ==================== A2A Message Handlers ====================
    
    async def _handle_track_decision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle decision tracking request from Game Master."""
        session_id = payload.get("session_id")
        decision_data = payload.get("decision_data", {})
        
        evaluation = await self.track_decision(session_id, decision_data)
        
        return {
            "session_id": session_id,
            "evaluation": evaluation,
            "tracked_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _handle_evaluate_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session evaluation request."""
        session_data = payload.get("session")
        if not session_data:
            logger.error(f"[{self.agent_name}] Missing session data in payload. Keys: {list(payload.keys())}")
            return {"error": "Missing session data"}
            
        try:
            # Reconstruct session object
            session = CyberGuardSession(**session_data)
            evaluation = await self.calculate_session_score(session)
            return evaluation
        except Exception as e:
            logger.error(f"[{self.agent_name}] Failed to reconstruct session: {e}")
            return {"error": str(e)}
    
    async def _handle_risk_assessment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle risk assessment request."""
        session_id = payload.get("session_id")
        
        session_metrics = self.evaluation_metrics.get(session_id, {})
        decisions = session_metrics.get("decisions", [])
        
        if not decisions:
            return {"risk_level": "unknown", "risk_score": 0.0}
        
        # Calculate current risk based on recent decisions
        recent_decisions = decisions[-5:]  # Last 5 decisions
        risk_impacts = [d["decision_point"]["risk_score_impact"] for d in recent_decisions]
        avg_risk = sum(risk_impacts) / len(risk_impacts)
        
        return {
            "session_id": session_id,
            "risk_score": round(avg_risk, 2),
            "risk_level": self._categorize_risk(avg_risk),
            "decisions_analyzed": len(recent_decisions)
        }
    
    async def _handle_difficulty_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle difficulty recommendation request."""
        session_id = payload.get("session_id")
        current_difficulty = DifficultyLevel(payload.get("current_difficulty", 3))
        
        session_metrics = self.evaluation_metrics.get(session_id, {})
        decisions = session_metrics.get("decisions", [])
        
        if len(decisions) < 3:  # Not enough data
            return {
                "recommendation": current_difficulty.value,
                "reason": "insufficient_data"
            }
        
        # Calculate success rate
        correct = sum(1 for d in decisions if d["evaluation"]["outcome"] == "correct")
        success_rate = correct / len(decisions)
        
        # Target 70% success rate for optimal learning
        if success_rate > 0.85:  # Too easy
            recommended = min(current_difficulty.value + 1, 5)
            reason = "user_performing_well"
        elif success_rate < 0.55:  # Too hard
            recommended = max(current_difficulty.value - 1, 1)
            reason = "user_struggling"
        else:
            recommended = current_difficulty.value
            reason = "optimal_difficulty"
        
        return {
            "session_id": session_id,
            "current_difficulty": current_difficulty.value,
            "recommended_difficulty": recommended,
            "success_rate": round(success_rate * 100, 1),
            "reason": reason
        }
    
    # ==================== Evaluation Calculation Methods ====================
    
    async def _evaluate_decision(
        self,
        decision: DecisionPoint,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a single decision point.
        
        Returns:
            Evaluation dictionary with outcome, risk_impact, and analysis
        """
        # Determine if decision was correct
        is_correct = decision.user_choice.lower() == decision.correct_choice.lower()
        
        # Get response time
        response_time = context.get("response_time", 30.0)
        
        # Calculate risk impact
        base_risk = 0.0 if is_correct else 1.0
        
        # Adjust for response time
        if response_time < self.time_thresholds["hasty"]:
            time_penalty = 0.1  # Acting too quickly
        elif response_time > self.time_thresholds["slow"]:
            time_penalty = 0.05  # Took too long
        else:
            time_penalty = 0.0
        
        risk_impact = min(1.0, base_risk + time_penalty)
        
        # Determine outcome category
        if is_correct and response_time < self.time_thresholds["optimal"]:
            outcome = "correct_quick"
        elif is_correct:
            outcome = "correct"
        elif response_time < self.time_thresholds["hasty"]:
            outcome = "incorrect_hasty"
        else:
            outcome = "incorrect"
        
        return {
            "outcome": outcome,
            "is_correct": is_correct,
            "risk_impact": risk_impact,
            "response_time": response_time,
            "time_category": self._categorize_response_time(response_time),
            "vulnerability": decision.vulnerability
        }
    
    async def _calculate_recognition_score(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate threat recognition score (0.0-1.0)."""
        if not decisions:
            return 0.0
        
        correct_count = sum(1 for d in decisions if d["evaluation"]["is_correct"])
        return correct_count / len(decisions)
    
    async def _calculate_response_time_score(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate response time quality score (0.0-1.0)."""
        if not decisions:
            return 0.0
        
        optimal_count = sum(
            1 for d in decisions
            if d["evaluation"]["time_category"] == "optimal"
        )
        
        return optimal_count / len(decisions)
    
    async def _calculate_action_quality_score(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate action quality score (0.0-1.0)."""
        if not decisions:
            return 0.0
        
        # Weight correct quick responses higher
        quality_sum = 0.0
        for decision in decisions:
            outcome = decision["evaluation"]["outcome"]
            if outcome == "correct_quick":
                quality_sum += 1.0
            elif outcome == "correct":
                quality_sum += 0.9
            elif outcome == "incorrect_hasty":
                quality_sum += 0.2  # At least they responded
            else:
                quality_sum += 0.0
        
        return quality_sum / len(decisions)
    
    async def _calculate_confidence_score(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate confidence calibration score (0.0-1.0)."""
        decisions_with_confidence = [
            d for d in decisions
            if d["decision_point"].get("confidence_level") is not None
        ]
        
        if not decisions_with_confidence:
            return 0.5  # Neutral score if no confidence data
        
        # Measure calibration: high confidence + correct = good
        calibrated_count = 0
        for decision in decisions_with_confidence:
            confidence = decision["decision_point"]["confidence_level"]
            is_correct = decision["evaluation"]["is_correct"]
            
            # Well calibrated if confidence matches correctness
            if (confidence > 0.7 and is_correct) or (confidence < 0.5 and not is_correct):
                calibrated_count += 1
        
        return calibrated_count / len(decisions_with_confidence)
    
    async def _analyze_vulnerability_patterns(
        self,
        decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze performance by vulnerability type.
        
        Returns:
            Dictionary mapping vulnerability types to performance metrics
        """
        vulnerability_stats: Dict[str, Dict[str, Any]] = {}
        
        for decision in decisions:
            vuln_type = decision["decision_point"]["vulnerability"]
            is_correct = decision["evaluation"]["is_correct"]
            
            if vuln_type not in vulnerability_stats:
                vulnerability_stats[vuln_type] = {
                    "attempts": 0,
                    "correct": 0,
                    "success_rate": 0.0
                }
            
            vulnerability_stats[vuln_type]["attempts"] += 1
            if is_correct:
                vulnerability_stats[vuln_type]["correct"] += 1
        
        # Calculate success rates
        for vuln_type, stats in vulnerability_stats.items():
            stats["success_rate"] = stats["correct"] / stats["attempts"]
        
        # Categorize as strengths or weaknesses
        strengths = [
            vuln for vuln, stats in vulnerability_stats.items()
            if stats["success_rate"] >= 0.8
        ]
        weaknesses = [
            vuln for vuln, stats in vulnerability_stats.items()
            if stats["success_rate"] < 0.6
        ]
        
        return {
            "by_type": vulnerability_stats,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    async def _identify_knowledge_gaps(
        self,
        decisions: List[Dict[str, Any]],
        vulnerability_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Identify specific knowledge gaps based on failure patterns."""
        gaps = []
        
        for vuln_type in vulnerability_analysis["weaknesses"]:
            stats = vulnerability_analysis["by_type"][vuln_type]
            gaps.append({
                "gap_type": vuln_type,
                "severity": "high" if stats["success_rate"] < 0.4 else "medium",
                "attempts": stats["attempts"],
                "success_rate": round(stats["success_rate"] * 100, 1)
            })
        
        return gaps
    
    async def _generate_recommendations(
        self,
        risk_score: float,
        vulnerability_analysis: Dict[str, Any],
        knowledge_gaps: List[Dict[str, str]]
    ) -> List[str]:
        """Generate actionable learning recommendations."""
        recommendations = []
        
        # Overall risk-based recommendations
        if risk_score > self.risk_thresholds["high"]:
            recommendations.append(
                "Consider reviewing fundamental security awareness training materials."
            )
        
        # Vulnerability-specific recommendations
        for gap in knowledge_gaps[:3]:  # Top 3 gaps
            vuln_type = gap["gap_type"]
            
            # Map vulnerability types to learning resources
            if "phishing" in vuln_type:
                recommendations.append(
                    f"Focus on {vuln_type} recognition training - "
                    f"current success rate: {gap['success_rate']}%"
                )
            elif "urgency" in vuln_type:
                recommendations.append(
                    "Practice identifying urgency-based social engineering tactics"
                )
            elif "authority" in vuln_type:
                recommendations.append(
                    "Learn to verify authority claims before taking action"
                )
        
        # Pattern-based recommendations
        if not recommendations:
            recommendations.append(
                "Continue current training path - showing consistent performance"
            )
        
        return recommendations
    
    async def _recommend_difficulty(
        self,
        overall_score: float,
        session: CyberGuardSession
    ) -> Dict[str, Any]:
        """Recommend difficulty adjustment for next session."""
        current_difficulty = session.current_difficulty
        
        # Target 70% success rate (0.7 overall score)
        if overall_score > 0.85:  # >85% - too easy
            recommended = min(current_difficulty.value + 1, 5)
            adjustment = "increase"
            reason = "User consistently exceeding expectations"
        elif overall_score < 0.55:  # <55% - too hard
            recommended = max(current_difficulty.value - 1, 1)
            adjustment = "decrease"
            reason = "User struggling with current difficulty"
        else:
            recommended = current_difficulty.value
            adjustment = "maintain"
            reason = "Optimal challenge level achieved"
        
        return {
            "current": current_difficulty.value,
            "recommended": recommended,
            "adjustment": adjustment,
            "reason": reason
        }
    
    # ==================== Utility Methods ====================
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk level based on score."""
        if risk_score >= self.risk_thresholds["critical"]:
            return "critical"
        elif risk_score >= self.risk_thresholds["high"]:
            return "high"
        elif risk_score >= self.risk_thresholds["medium"]:
            return "medium"
        elif risk_score >= self.risk_thresholds["low"]:
            return "low"
        else:
            return "minimal"
    
    def _categorize_response_time(self, response_time: float) -> str:
        """Categorize response time quality."""
        if response_time < self.time_thresholds["hasty"]:
            return "hasty"
        elif response_time <= self.time_thresholds["optimal"]:
            return "optimal"
        elif response_time <= self.time_thresholds["slow"]:
            return "deliberate"
        else:
            return "slow"
    
    def _generate_empty_evaluation(self) -> Dict[str, Any]:
        """Generate placeholder evaluation when no data is available."""
        return {
            "overall_score": 0.0,
            "risk_score": 0.0,
            "risk_level": "unknown",
            "component_scores": {
                "recognition": 0.0,
                "response_time": 0.0,
                "action_quality": 0.0,
                "confidence": 0.0
            },
            "decisions_tracked": 0,
            "vulnerability_analysis": {"by_type": {}, "strengths": [], "weaknesses": []},
            "knowledge_gaps": [],
            "recommendations": ["Complete more scenarios to generate meaningful insights"],
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def _load_evaluation_criteria(self) -> None:
        """Load evaluation criteria and models."""
        # In production, this would load ML models or detailed rubrics
        logger.debug(f"[{self.agent_name}] Evaluation criteria loaded")
    
    async def _persist_pending_evaluations(self) -> None:
        """Persist any pending evaluations before shutdown."""
        if self.evaluation_metrics:
            logger.debug(
                f"[{self.agent_name}] Persisting {len(self.evaluation_metrics)} evaluations"
            )
            # In production, save to database or file storage
