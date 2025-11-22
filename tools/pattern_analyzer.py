#!/usr/bin/env python3
"""
Pattern Analyzer Tool - CyberGuard Academy

Analyzes user vulnerability patterns and learning behaviors
to identify areas for improvement and personalize training.

Key Features:
- Vulnerability pattern detection
- Learning behavior analysis
- Performance trend tracking
- Weakness identification
- Strength recognition
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from loguru import logger

from cyberguard.models import UserRole, DifficultyLevel, SocialEngineeringPattern
from cyberguard.config import Settings


class PatternAnalyzer:
    """
    Analyzes user patterns to identify vulnerabilities and learning trends.
    
    Tracks user decisions, identifies recurring vulnerabilities,
    and provides insights for personalized training adaptation.
    """
    
    def __init__(self):
        self.settings = Settings()
        self.patterns_path = Path("data/patterns")
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        
        # Pattern recognition thresholds
        self.vulnerability_threshold = 0.3  # Below 30% success rate = vulnerability
        self.strength_threshold = 0.8      # Above 80% success rate = strength
        self.trend_window_days = 14        # Analyze last 14 days for trends
        
        logger.info("[PatternAnalyzer] Pattern analyzer created")
    
    async def initialize(self) -> None:
        """
        Initialize pattern analyzer and load existing analysis data.
        """
        logger.info("[PatternAnalyzer] Initializing pattern analyzer...")
        
        try:
            # Create patterns directory
            self.patterns_path.mkdir(parents=True, exist_ok=True)
            
            # Load recent analysis data into cache
            await self._load_recent_analyses()
            
            logger.info("[PatternAnalyzer] Pattern analyzer initialized")
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to initialize: {e}")
            raise
    
    async def shutdown(self) -> None:
        """
        Shutdown pattern analyzer and save cached data.
        """
        logger.info("[PatternAnalyzer] Shutting down pattern analyzer...")
        
        try:
            # Save all cached analyses
            for user_id, analysis in self.analysis_cache.items():
                await self._save_analysis(user_id, analysis)
            
            # Clear cache
            self.analysis_cache.clear()
            
            logger.info("[PatternAnalyzer] Pattern analyzer shutdown complete")
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Error during shutdown: {e}")
    
    async def analyze_patterns(
        self,
        user_id: str,
        decisions: List[Dict[str, Any]],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive pattern analysis for a user.
        
        Args:
            user_id: User identifier
            decisions: List of recent user decisions
            profile: User profile data
            
        Returns:
            Dictionary containing pattern analysis results
        """
        logger.info(f"[PatternAnalyzer] Analyzing patterns for user: {user_id[:8]}...")
        
        try:
            # Load existing analysis or create new
            existing_analysis = await self._load_analysis(user_id)
            
            # Perform different types of analysis
            vulnerability_patterns = await self._analyze_vulnerabilities(decisions, profile)
            behavioral_patterns = await self._analyze_behavior(decisions, profile)
            learning_trends = await self._analyze_learning_trends(decisions, existing_analysis)
            performance_patterns = await self._analyze_performance(decisions, profile)
            
            # Combine analysis results
            analysis = {
                "user_id": user_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "vulnerability_patterns": vulnerability_patterns,
                "behavioral_patterns": behavioral_patterns,
                "learning_trends": learning_trends,
                "performance_patterns": performance_patterns,
                "recommendations": await self._generate_recommendations(
                    vulnerability_patterns, 
                    behavioral_patterns, 
                    learning_trends,
                    profile
                ),
                "risk_assessment": await self._assess_risk_level(
                    vulnerability_patterns,
                    performance_patterns,
                    profile
                )
            }
            
            # Cache and save analysis
            self.analysis_cache[user_id] = analysis
            await self._save_analysis(user_id, analysis)
            
            logger.info(f"[PatternAnalyzer] Completed analysis for user: {user_id[:8]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to analyze patterns for {user_id[:8]}...: {e}")
            raise
    
    async def get_recent_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get recent vulnerability patterns for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of recent patterns
        """
        try:
            analysis = await self._load_analysis(user_id)
            
            if analysis:
                return analysis.get("vulnerability_patterns", {}).get("recent_patterns", [])
            
            return []
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to get recent patterns: {e}")
            return []
    
    async def identify_focus_areas(self, user_id: str) -> List[str]:
        """
        Identify key areas where user needs focused training.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of focus area identifiers
        """
        try:
            analysis = await self._load_analysis(user_id)
            
            if not analysis:
                return ["basic_phishing_recognition"]  # Default for new users
            
            vulnerabilities = analysis.get("vulnerability_patterns", {})
            weak_areas = vulnerabilities.get("weak_threat_types", [])
            
            # Priority order: critical vulnerabilities first
            focus_areas = []
            
            # Add critical vulnerabilities (success rate < 0.2)
            for area in weak_areas:
                if area.get("success_rate", 1.0) < 0.2:
                    focus_areas.append(area.get("threat_type", "unknown"))
            
            # Add moderate vulnerabilities if we have space
            for area in weak_areas:
                if 0.2 <= area.get("success_rate", 1.0) < self.vulnerability_threshold:
                    if area.get("threat_type", "unknown") not in focus_areas:
                        focus_areas.append(area.get("threat_type", "unknown"))
            
            return focus_areas[:3]  # Return top 3 focus areas
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to identify focus areas: {e}")
            return ["basic_phishing_recognition"]
    
    # Analysis Methods
    
    async def _analyze_vulnerabilities(
        self, 
        decisions: List[Dict[str, Any]], 
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze vulnerability patterns in user decisions."""
        try:
            threat_type_performance = {}
            social_eng_performance = {}
            
            # Group decisions by threat type and social engineering pattern
            for decision in decisions:
                threat_type = decision.get("vulnerability_type", "unknown")
                social_pattern = decision.get("social_eng_pattern", "unknown")
                correct = decision.get("correct_choice") == decision.get("user_choice")
                
                # Track threat type performance
                if threat_type not in threat_type_performance:
                    threat_type_performance[threat_type] = {"correct": 0, "total": 0}
                
                threat_type_performance[threat_type]["total"] += 1
                if correct:
                    threat_type_performance[threat_type]["correct"] += 1
                
                # Track social engineering pattern performance
                if social_pattern not in social_eng_performance:
                    social_eng_performance[social_pattern] = {"correct": 0, "total": 0}
                
                social_eng_performance[social_pattern]["total"] += 1
                if correct:
                    social_eng_performance[social_pattern]["correct"] += 1
            
            # Calculate success rates and identify vulnerabilities
            weak_threat_types = []
            strong_threat_types = []
            
            for threat_type, stats in threat_type_performance.items():
                if stats["total"] > 0:
                    success_rate = stats["correct"] / stats["total"]
                    
                    threat_analysis = {
                        "threat_type": threat_type,
                        "success_rate": success_rate,
                        "attempts": stats["total"],
                        "successful": stats["correct"]
                    }
                    
                    if success_rate < self.vulnerability_threshold:
                        weak_threat_types.append(threat_analysis)
                    elif success_rate > self.strength_threshold:
                        strong_threat_types.append(threat_analysis)
            
            # Sort by success rate (weakest first for vulnerabilities)
            weak_threat_types.sort(key=lambda x: x["success_rate"])
            strong_threat_types.sort(key=lambda x: x["success_rate"], reverse=True)
            
            return {
                "weak_threat_types": weak_threat_types,
                "strong_threat_types": strong_threat_types,
                "social_eng_vulnerabilities": self._analyze_social_eng_vulnerabilities(social_eng_performance),
                "recent_patterns": self._identify_recent_patterns(decisions)
            }
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to analyze vulnerabilities: {e}")
            return {}
    
    async def _analyze_behavior(
        self, 
        decisions: List[Dict[str, Any]], 
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze behavioral patterns in user responses."""
        try:
            if not decisions:
                return {}
            
            # Response time analysis
            response_times = [d.get("response_time", 0) for d in decisions if d.get("response_time", 0) > 0]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Confidence patterns
            confidence_levels = [d.get("confidence_level", 0.5) for d in decisions if d.get("confidence_level")]
            avg_confidence = sum(confidence_levels) / len(confidence_levels) if confidence_levels else 0.5
            
            # Decision patterns
            hasty_decisions = len([d for d in decisions if d.get("response_time", 0) < 10])  # < 10 seconds
            careful_decisions = len([d for d in decisions if d.get("response_time", 0) > 60])  # > 1 minute
            
            # Risk tolerance
            risky_choices = len([d for d in decisions if d.get("risk_level", "medium") == "high"])
            safe_choices = len([d for d in decisions if d.get("risk_level", "medium") == "low"])
            
            return {
                "response_patterns": {
                    "average_response_time": avg_response_time,
                    "hasty_decision_rate": hasty_decisions / len(decisions) if decisions else 0,
                    "careful_decision_rate": careful_decisions / len(decisions) if decisions else 0
                },
                "confidence_patterns": {
                    "average_confidence": avg_confidence,
                    "overconfidence_rate": len([d for d in decisions 
                                              if d.get("confidence_level", 0.5) > 0.8 and 
                                              d.get("correct_choice") != d.get("user_choice")]) / len(decisions) if decisions else 0
                },
                "risk_tolerance": {
                    "risky_choice_rate": risky_choices / len(decisions) if decisions else 0,
                    "safe_choice_rate": safe_choices / len(decisions) if decisions else 0
                }
            }
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to analyze behavior: {e}")
            return {}
    
    async def _analyze_learning_trends(
        self, 
        decisions: List[Dict[str, Any]], 
        existing_analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze learning progression and trends."""
        try:
            if len(decisions) < 5:
                return {"trend": "insufficient_data", "improvement_rate": 0.0}
            
            # Sort decisions by timestamp
            sorted_decisions = sorted(decisions, key=lambda x: x.get("timestamp", ""))
            
            # Calculate rolling success rate
            window_size = min(5, len(sorted_decisions))
            success_rates = []
            
            for i in range(window_size, len(sorted_decisions) + 1):
                window = sorted_decisions[i-window_size:i]
                correct = sum(1 for d in window if d.get("correct_choice") == d.get("user_choice"))
                success_rates.append(correct / window_size)
            
            if len(success_rates) < 2:
                return {"trend": "insufficient_data", "improvement_rate": 0.0}
            
            # Calculate trend
            early_rate = sum(success_rates[:len(success_rates)//2]) / (len(success_rates)//2)
            recent_rate = sum(success_rates[len(success_rates)//2:]) / (len(success_rates) - len(success_rates)//2)
            
            improvement_rate = recent_rate - early_rate
            
            if improvement_rate > 0.1:
                trend = "improving"
            elif improvement_rate < -0.1:
                trend = "declining"
            else:
                trend = "stable"
            
            return {
                "trend": trend,
                "improvement_rate": improvement_rate,
                "early_success_rate": early_rate,
                "recent_success_rate": recent_rate,
                "consistency": self._calculate_consistency(success_rates)
            }
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to analyze learning trends: {e}")
            return {}
    
    async def _analyze_performance(
        self, 
        decisions: List[Dict[str, Any]], 
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze overall performance patterns."""
        try:
            if not decisions:
                return {}
            
            correct_decisions = sum(1 for d in decisions if d.get("correct_choice") == d.get("user_choice"))
            overall_success_rate = correct_decisions / len(decisions)
            
            # Performance by difficulty
            difficulty_performance = {}
            for decision in decisions:
                difficulty = decision.get("difficulty", 3)
                if difficulty not in difficulty_performance:
                    difficulty_performance[difficulty] = {"correct": 0, "total": 0}
                
                difficulty_performance[difficulty]["total"] += 1
                if decision.get("correct_choice") == decision.get("user_choice"):
                    difficulty_performance[difficulty]["correct"] += 1
            
            # Calculate performance by difficulty
            difficulty_rates = {}
            for diff, stats in difficulty_performance.items():
                if stats["total"] > 0:
                    difficulty_rates[diff] = stats["correct"] / stats["total"]
            
            return {
                "overall_success_rate": overall_success_rate,
                "difficulty_performance": difficulty_rates,
                "performance_consistency": self._calculate_performance_consistency(decisions),
                "learning_efficiency": self._calculate_learning_efficiency(decisions)
            }
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to analyze performance: {e}")
            return {}
    
    # Helper Methods
    
    def _analyze_social_eng_vulnerabilities(self, social_eng_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze vulnerabilities to specific social engineering patterns."""
        vulnerabilities = []
        
        for pattern, stats in social_eng_performance.items():
            if stats["total"] > 0:
                success_rate = stats["correct"] / stats["total"]
                
                if success_rate < self.vulnerability_threshold:
                    vulnerabilities.append({
                        "pattern": pattern,
                        "success_rate": success_rate,
                        "attempts": stats["total"],
                        "vulnerability_level": "high" if success_rate < 0.2 else "moderate"
                    })
        
        return sorted(vulnerabilities, key=lambda x: x["success_rate"])
    
    def _identify_recent_patterns(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify patterns in recent decisions."""
        # Get decisions from last 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_decisions = []
        
        for decision in decisions:
            try:
                decision_date = datetime.fromisoformat(decision.get("timestamp", ""))
                if decision_date >= cutoff_date:
                    recent_decisions.append(decision)
            except:
                continue  # Skip decisions with invalid timestamps
        
        if len(recent_decisions) < 3:
            return []
        
        # Analyze patterns in recent decisions
        patterns = []
        
        # Pattern: Consistent mistakes in specific threat types
        threat_mistakes = {}
        for decision in recent_decisions:
            if decision.get("correct_choice") != decision.get("user_choice"):
                threat_type = decision.get("vulnerability_type", "unknown")
                threat_mistakes[threat_type] = threat_mistakes.get(threat_type, 0) + 1
        
        for threat_type, mistake_count in threat_mistakes.items():
            if mistake_count >= 2:  # At least 2 mistakes
                patterns.append({
                    "type": "recurring_vulnerability",
                    "threat_type": threat_type,
                    "frequency": mistake_count,
                    "severity": "high" if mistake_count >= 3 else "moderate"
                })
        
        return patterns
    
    def _calculate_consistency(self, success_rates: List[float]) -> float:
        """Calculate consistency score based on success rate variance."""
        if len(success_rates) < 2:
            return 0.5
        
        # Calculate variance
        mean_rate = sum(success_rates) / len(success_rates)
        variance = sum((rate - mean_rate) ** 2 for rate in success_rates) / len(success_rates)
        
        # Convert variance to consistency score (lower variance = higher consistency)
        # Normalize to 0-1 scale
        consistency = max(0.0, min(1.0, 1.0 - (variance * 4)))  # Scale factor of 4
        
        return consistency
    
    def _calculate_performance_consistency(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate how consistent user performance is across different scenarios."""
        if len(decisions) < 5:
            return 0.5
        
        # Group by scenario type and calculate success rates
        scenario_performance = {}
        
        for decision in decisions:
            scenario_type = decision.get("vulnerability_type", "unknown")
            if scenario_type not in scenario_performance:
                scenario_performance[scenario_type] = {"correct": 0, "total": 0}
            
            scenario_performance[scenario_type]["total"] += 1
            if decision.get("correct_choice") == decision.get("user_choice"):
                scenario_performance[scenario_type]["correct"] += 1
        
        # Calculate success rates for each scenario type
        success_rates = []
        for scenario_type, stats in scenario_performance.items():
            if stats["total"] >= 2:  # Only include scenarios with at least 2 attempts
                success_rates.append(stats["correct"] / stats["total"])
        
        return self._calculate_consistency(success_rates)
    
    def _calculate_learning_efficiency(self, decisions: List[Dict[str, Any]]) -> float:
        """Calculate how efficiently the user learns from mistakes."""
        if len(decisions) < 10:
            return 0.5
        
        # Look at improvement after mistakes
        improvement_scores = []
        
        for i in range(len(decisions) - 3):
            # Check if user made a mistake
            if decisions[i].get("correct_choice") != decisions[i].get("user_choice"):
                threat_type = decisions[i].get("vulnerability_type", "unknown")
                
                # Look at next 3 decisions of the same type
                subsequent_decisions = []
                for j in range(i + 1, min(i + 4, len(decisions))):
                    if decisions[j].get("vulnerability_type", "unknown") == threat_type:
                        subsequent_decisions.append(decisions[j])
                
                # Calculate improvement
                if subsequent_decisions:
                    correct_after = sum(1 for d in subsequent_decisions 
                                      if d.get("correct_choice") == d.get("user_choice"))
                    improvement_scores.append(correct_after / len(subsequent_decisions))
        
        if not improvement_scores:
            return 0.5
        
        return sum(improvement_scores) / len(improvement_scores)
    
    async def _generate_recommendations(
        self,
        vulnerability_patterns: Dict[str, Any],
        behavioral_patterns: Dict[str, Any],
        learning_trends: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> List[str]:
        """Generate training recommendations based on pattern analysis."""
        recommendations = []
        
        # Vulnerability-based recommendations
        weak_areas = vulnerability_patterns.get("weak_threat_types", [])
        if weak_areas:
            for area in weak_areas[:2]:  # Top 2 weakest areas
                recommendations.append(f"Focus on {area['threat_type']} recognition training")
        
        # Behavioral recommendations
        response_patterns = behavioral_patterns.get("response_patterns", {})
        if response_patterns.get("hasty_decision_rate", 0) > 0.3:
            recommendations.append("Practice taking more time to analyze suspicious emails")
        
        confidence_patterns = behavioral_patterns.get("confidence_patterns", {})
        if confidence_patterns.get("overconfidence_rate", 0) > 0.2:
            recommendations.append("Work on verification techniques before making decisions")
        
        # Learning trend recommendations
        trend = learning_trends.get("trend", "stable")
        if trend == "declining":
            recommendations.append("Review basic security awareness principles")
        elif trend == "stable":
            recommendations.append("Try more challenging scenarios to continue improvement")
        
        return recommendations[:5]  # Return top 5 recommendations
    
    async def _assess_risk_level(
        self,
        vulnerability_patterns: Dict[str, Any],
        performance_patterns: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> str:
        """Assess overall cybersecurity risk level for the user."""
        try:
            risk_factors = []
            
            # Check critical vulnerabilities
            weak_areas = vulnerability_patterns.get("weak_threat_types", [])
            critical_weaknesses = [area for area in weak_areas if area.get("success_rate", 1.0) < 0.2]
            
            if critical_weaknesses:
                risk_factors.append("critical_vulnerabilities")
            
            # Check overall performance
            overall_success = performance_patterns.get("overall_success_rate", 0.5)
            if overall_success < 0.4:
                risk_factors.append("poor_overall_performance")
            elif overall_success < 0.6:
                risk_factors.append("moderate_performance")
            
            # Check consistency
            consistency = performance_patterns.get("performance_consistency", 0.5)
            if consistency < 0.3:
                risk_factors.append("inconsistent_performance")
            
            # Determine risk level
            if "critical_vulnerabilities" in risk_factors or "poor_overall_performance" in risk_factors:
                return "high"
            elif len(risk_factors) >= 2:
                return "moderate"
            elif len(risk_factors) == 1:
                return "low"
            else:
                return "minimal"
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to assess risk level: {e}")
            return "unknown"
    
    # Storage Methods
    
    async def _load_analysis(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load pattern analysis from storage."""
        try:
            # Check cache first
            if user_id in self.analysis_cache:
                return self.analysis_cache[user_id]
            
            # Load from file
            analysis_file = self.patterns_path / f"{user_id}_analysis.json"
            
            if not analysis_file.exists():
                return None
            
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
            
            # Cache for future use
            self.analysis_cache[user_id] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to load analysis for {user_id[:8]}...: {e}")
            return None
    
    async def _save_analysis(self, user_id: str, analysis: Dict[str, Any]) -> None:
        """Save pattern analysis to storage."""
        try:
            analysis_file = self.patterns_path / f"{user_id}_analysis.json"
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"[PatternAnalyzer] Failed to save analysis for {user_id[:8]}...: {e}")
            raise
    
    async def _load_recent_analyses(self) -> None:
        """Load recent analyses into cache."""
        try:
            # Load analyses accessed in last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for analysis_file in self.patterns_path.glob("*_analysis.json"):
                if analysis_file.stat().st_mtime > cutoff_time.timestamp():
                    user_id = analysis_file.stem.replace("_analysis", "")
                    analysis = await self._load_analysis(user_id)
                    if analysis:
                        self.analysis_cache[user_id] = analysis
            
            logger.debug(f"[PatternAnalyzer] Loaded {len(self.analysis_cache)} recent analyses into cache")
            
        except Exception as e:
            logger.warning(f"[PatternAnalyzer] Failed to load recent analyses: {e}")