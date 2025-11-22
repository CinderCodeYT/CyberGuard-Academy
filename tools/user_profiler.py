#!/usr/bin/env python3
"""
User Profiler Tool - CyberGuard Academy

Manages user learning profiles and tracks skills progression.
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger

from cyberguard.models import UserRole, DifficultyLevel
from cyberguard.config import Settings


class UserProfiler:
    """Manages user learning profiles and personalized training data."""
    
    def __init__(self):
        self.settings = Settings()
        self.profiles_path = Path("data/profiles")
        self.profile_cache: Dict[str, Dict[str, Any]] = {}
        logger.info("[UserProfiler] User profiler created")
    
    async def initialize(self) -> None:
        """Initialize user profiler and load existing profiles."""
        logger.info("[UserProfiler] Initializing user profiler...")
        
        try:
            self.profiles_path.mkdir(parents=True, exist_ok=True)
            await self._load_recent_profiles()
            logger.info("[UserProfiler] User profiler initialized")
        except Exception as e:
            logger.error(f"[UserProfiler] Failed to initialize: {e}")
            raise
    
    async def shutdown(self) -> None:
        """Shutdown user profiler and save cached profiles."""
        logger.info("[UserProfiler] Shutting down user profiler...")
        
        try:
            for user_id, profile in self.profile_cache.items():
                await self._save_profile(user_id, profile)
            self.profile_cache.clear()
            logger.info("[UserProfiler] User profiler shutdown complete")
        except Exception as e:
            logger.error(f"[UserProfiler] Error during shutdown: {e}")
    
    async def create_profile(self, user_id: str, user_role: UserRole) -> Dict[str, Any]:
        """Create a new user learning profile with default settings."""
        logger.info(f"[UserProfiler] Creating profile for user: {user_id[:8]}...")
        
        try:
            profile = {
                "user_id": user_id,
                "user_role": user_role.value,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "learning_preferences": self._get_default_preferences(user_role),
                "skill_assessments": self._get_initial_skill_assessments(user_role),
                "performance_history": {
                    "sessions_completed": 0,
                    "total_scenarios": 0,
                    "successful_identifications": 0,
                    "missed_threats": 0,
                    "false_positives": 0,
                    "average_response_time": 0.0,
                    "improvement_trend": "new_user"
                },
                "vulnerability_patterns": {
                    "weak_areas": [],
                    "strong_areas": [],
                    "recent_mistakes": [],
                    "learning_goals": self._get_initial_learning_goals(user_role)
                },
                "adaptation_settings": {
                    "current_difficulty": self.settings.default_difficulty_level,
                    "auto_adapt_difficulty": True,
                    "scenario_frequency": "weekly",
                    "reminder_preferences": {
                        "email_reminders": True,
                        "progress_reports": True,
                        "achievement_notifications": True
                    }
                }
            }
            
            await self._save_profile(user_id, profile)
            self.profile_cache[user_id] = profile
            
            logger.info(f"[UserProfiler] Created profile for user: {user_id[:8]}...")
            return profile
            
        except Exception as e:
            logger.error(f"[UserProfiler] Failed to create profile for {user_id[:8]}...: {e}")
            raise
    
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user profile, loading from storage if needed."""
        if user_id in self.profile_cache:
            return self.profile_cache[user_id]
        
        profile = await self._load_profile(user_id)
        if profile:
            self.profile_cache[user_id] = profile
        
        return profile
    
    async def update_profile(
        self,
        user_id: str,
        updates: Dict[str, Any],
        merge: bool = True
    ) -> bool:
        """Update user profile with new data."""
        try:
            profile = await self.get_profile(user_id)
            
            if not profile:
                logger.warning(f"[UserProfiler] Profile not found for user: {user_id[:8]}...")
                return False
            
            if merge:
                profile = self._deep_merge(profile, updates)
            else:
                profile.update(updates)
            
            profile["last_updated"] = datetime.now().isoformat()
            
            await self._save_profile(user_id, profile)
            self.profile_cache[user_id] = profile
            
            logger.debug(f"[UserProfiler] Updated profile for user: {user_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"[UserProfiler] Failed to update profile for {user_id[:8]}...: {e}")
            return False
    
    async def get_learning_recommendations(self, user_id: str) -> Dict[str, Any]:
        """Generate personalized learning recommendations for user."""
        try:
            profile = await self.get_profile(user_id)
            if not profile:
                return {}
            
            recommendations = {
                "difficulty_adjustment": await self._recommend_difficulty_adjustment(profile),
                "focus_areas": profile["vulnerability_patterns"]["weak_areas"][:3],
                "next_scenarios": await self._recommend_scenario_types(profile),
                "learning_path": await self._generate_learning_path(profile),
                "estimated_improvement_time": await self._estimate_improvement_time(profile)
            }
            
            return recommendations
            
        except Exception as e:
            logger.error(f"[UserProfiler] Failed to generate recommendations: {e}")
            return {}
    
    # Private Helper Methods
    
    async def _load_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user profile from storage."""
        try:
            profile_file = self.profiles_path / f"{user_id}.json"
            
            if not profile_file.exists():
                return None
            
            with open(profile_file, 'r') as f:
                profile = json.load(f)
            
            return profile
            
        except Exception as e:
            logger.error(f"[UserProfiler] Failed to load profile for {user_id[:8]}...: {e}")
            return None
    
    async def _save_profile(self, user_id: str, profile: Dict[str, Any]) -> None:
        """Save user profile to storage."""
        try:
            profile_file = self.profiles_path / f"{user_id}.json"
            
            with open(profile_file, 'w') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"[UserProfiler] Failed to save profile for {user_id[:8]}...: {e}")
            raise
    
    async def _load_recent_profiles(self) -> None:
        """Load recently accessed profiles into cache."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for profile_file in self.profiles_path.glob("*.json"):
                if profile_file.stat().st_mtime > cutoff_time.timestamp():
                    user_id = profile_file.stem
                    profile = await self._load_profile(user_id)
                    if profile:
                        self.profile_cache[user_id] = profile
            
            logger.debug(f"[UserProfiler] Loaded {len(self.profile_cache)} recent profiles into cache")
            
        except Exception as e:
            logger.warning(f"[UserProfiler] Failed to load recent profiles: {e}")
    
    def _get_default_preferences(self, user_role: UserRole) -> Dict[str, Any]:
        """Get default learning preferences based on user role."""
        role_defaults = {
            UserRole.GENERAL: {
                "preferred_difficulty": 2,
                "learning_pace": "normal",
                "feedback_style": "immediate",
                "scenario_types": ["urgency", "curiosity"]
            },
            UserRole.FINANCE: {
                "preferred_difficulty": 3,
                "learning_pace": "normal",
                "feedback_style": "summary",
                "scenario_types": ["authority", "urgency"]
            },
            UserRole.IT_ADMIN: {
                "preferred_difficulty": 4,
                "learning_pace": "fast",
                "feedback_style": "minimal",
                "scenario_types": ["curiosity", "fear"]
            },
            UserRole.EXECUTIVE: {
                "preferred_difficulty": 3,
                "learning_pace": "normal",
                "feedback_style": "summary",
                "scenario_types": ["authority", "trust"]
            }
        }
        
        return role_defaults.get(user_role, role_defaults[UserRole.GENERAL])
    
    def _get_initial_skill_assessments(self, user_role: UserRole) -> Dict[str, float]:
        """Get initial skill assessment scores based on user role."""
        role_skills = {
            UserRole.GENERAL: {
                "phishing_recognition": 0.3,
                "link_verification": 0.2,
                "sender_authentication": 0.2,
                "social_engineering_awareness": 0.3,
                "overall_security_awareness": 0.25
            },
            UserRole.FINANCE: {
                "phishing_recognition": 0.4,
                "link_verification": 0.3,
                "sender_authentication": 0.3,
                "social_engineering_awareness": 0.4,
                "overall_security_awareness": 0.35
            },
            UserRole.IT_ADMIN: {
                "phishing_recognition": 0.6,
                "link_verification": 0.7,
                "sender_authentication": 0.6,
                "social_engineering_awareness": 0.5,
                "overall_security_awareness": 0.6
            },
            UserRole.EXECUTIVE: {
                "phishing_recognition": 0.4,
                "link_verification": 0.3,
                "sender_authentication": 0.4,
                "social_engineering_awareness": 0.5,
                "overall_security_awareness": 0.4
            }
        }
        
        return role_skills.get(user_role, role_skills[UserRole.GENERAL])
    
    def _get_initial_learning_goals(self, user_role: UserRole) -> List[str]:
        """Get initial learning goals based on user role."""
        role_goals = {
            UserRole.GENERAL: [
                "recognize_phishing_emails",
                "verify_suspicious_links",
                "understand_social_engineering"
            ],
            UserRole.FINANCE: [
                "detect_payment_fraud",
                "verify_authority_requests",
                "secure_financial_communications"
            ],
            UserRole.IT_ADMIN: [
                "advanced_threat_detection",
                "email_authentication_analysis",
                "security_incident_response"
            ],
            UserRole.EXECUTIVE: [
                "executive_targeted_attacks",
                "business_email_compromise",
                "strategic_security_awareness"
            ]
        }
        
        return role_goals.get(user_role, role_goals[UserRole.GENERAL])
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    async def _recommend_difficulty_adjustment(self, profile: Dict[str, Any]) -> str:
        """Recommend difficulty adjustment based on user performance."""
        history = profile["performance_history"]
        
        if history["sessions_completed"] < 3:
            return "maintain"
        
        total_attempts = history["successful_identifications"] + history["missed_threats"]
        if total_attempts == 0:
            return "maintain"
        
        success_rate = history["successful_identifications"] / total_attempts
        target_rate = self.settings.target_success_rate
        
        if success_rate > target_rate + 0.15:
            return "increase"
        elif success_rate < target_rate - 0.15:
            return "decrease"
        else:
            return "maintain"
    
    async def _recommend_scenario_types(self, profile: Dict[str, Any]) -> List[str]:
        """Recommend scenario types based on weak areas and preferences."""
        weak_areas = profile["vulnerability_patterns"]["weak_areas"]
        preferences = profile["learning_preferences"]["scenario_types"]
        
        recommendations = []
        
        # Add weak areas first (need improvement)
        recommendations.extend(weak_areas[:2])
        
        # Add preferred types that aren't already included
        for pref in preferences:
            if pref not in recommendations:
                recommendations.append(pref)
        
        return recommendations[:4]
    
    async def _generate_learning_path(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized learning path for user."""
        weak_areas = profile["vulnerability_patterns"]["weak_areas"]
        skill_level = profile["skill_assessments"]["overall_security_awareness"]
        
        if skill_level < 0.3:
            path = {
                "current_stage": "basic_awareness",
                "next_objectives": ["recognize_obvious_phishing", "understand_email_safety"],
                "estimated_duration": "2-3 weeks",
                "focus_areas": weak_areas[:2] if weak_areas else ["phishing_recognition"]
            }
        elif skill_level < 0.6:
            path = {
                "current_stage": "threat_identification",
                "next_objectives": ["advanced_phishing_detection", "link_verification"],
                "estimated_duration": "3-4 weeks",
                "focus_areas": weak_areas[:3] if weak_areas else ["sender_authentication"]
            }
        else:
            path = {
                "current_stage": "security_mastery",
                "next_objectives": ["sophisticated_attack_recognition", "incident_response"],
                "estimated_duration": "4-6 weeks",
                "focus_areas": weak_areas if weak_areas else ["advanced_techniques"]
            }
        
        return path
    
    async def _estimate_improvement_time(self, profile: Dict[str, Any]) -> str:
        """Estimate time for user to show improvement."""
        improvement_trend = profile["performance_history"]["improvement_trend"]
        learning_pace = profile["learning_preferences"]["learning_pace"]
        
        base_time = {
            "fast": 1,
            "normal": 2,
            "slow": 3
        }.get(learning_pace, 2)
        
        trend_multiplier = {
            "strong": 0.5,
            "improving": 1.0,
            "stable": 1.5,
            "needs_attention": 2.0,
            "new_user": 1.0
        }.get(improvement_trend, 1.0)
        
        estimated_weeks = int(base_time * trend_multiplier)
        
        if estimated_weeks <= 1:
            return "1-2 weeks"
        elif estimated_weeks <= 2:
            return "2-3 weeks"
        elif estimated_weeks <= 4:
            return "3-4 weeks"
        else:
            return "4+ weeks"