#!/usr/bin/env python3
"""
Progress Tracker Tool - CyberGuard Academy

Tracks user learning progress, achievements, and milestones
to provide feedback and motivation for continued improvement.

Key Features:
- Learning milestone tracking
- Achievement system
- Progress visualization data
- Goal setting and tracking
- Performance metrics
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from loguru import logger

from cyberguard.models import UserRole, DifficultyLevel
from cyberguard.config import Settings


class ProgressTracker:
    """
    Tracks user learning progress and achievements.
    
    Monitors user advancement through training modules,
    tracks achievements, and provides progress metrics.
    """
    
    def __init__(self):
        self.settings = Settings()
        self.progress_path = Path("data/progress")
        self.progress_cache: Dict[str, Dict[str, Any]] = {}
        
        # Achievement definitions
        self.achievements = {
            "first_threat_identified": {
                "name": "First Success",
                "description": "Successfully identified your first phishing threat",
                "points": 10
            },
            "streak_3": {
                "name": "Getting Good",
                "description": "Correctly identified 3 threats in a row",
                "points": 25
            },
            "streak_5": {
                "name": "On Fire",
                "description": "Correctly identified 5 threats in a row",
                "points": 50
            },
            "streak_10": {
                "name": "Security Expert",
                "description": "Correctly identified 10 threats in a row",
                "points": 100
            },
            "phishing_master": {
                "name": "Phishing Master",
                "description": "Achieved 90% success rate on phishing scenarios",
                "points": 150
            },
            "speed_demon": {
                "name": "Quick Thinker",
                "description": "Average response time under 15 seconds",
                "points": 75
            },
            "thorough_analyzer": {
                "name": "Thorough Analyzer",
                "description": "Spent appropriate time analyzing complex threats",
                "points": 50
            },
            "milestone_10": {
                "name": "Getting Started",
                "description": "Completed 10 training scenarios",
                "points": 30
            },
            "milestone_50": {
                "name": "Experienced",
                "description": "Completed 50 training scenarios",
                "points": 100
            },
            "milestone_100": {
                "name": "Veteran",
                "description": "Completed 100 training scenarios",
                "points": 200
            }
        }
        
        logger.info("[ProgressTracker] Progress tracker created")
    
    async def initialize(self) -> None:
        """
        Initialize progress tracker and load existing data.
        """
        logger.info("[ProgressTracker] Initializing progress tracker...")
        
        try:
            # Create progress directory
            self.progress_path.mkdir(parents=True, exist_ok=True)
            
            # Load recent progress data into cache
            await self._load_recent_progress()
            
            logger.info("[ProgressTracker] Progress tracker initialized")
            
        except Exception as e:
            logger.error(f"[ProgressTracker] Failed to initialize: {e}")
            raise
    
    async def shutdown(self) -> None:
        """
        Shutdown progress tracker and save cached data.
        """
        logger.info("[ProgressTracker] Shutting down progress tracker...")
        
        try:
            # Save all cached progress
            for user_id, progress in self.progress_cache.items():
                await self._save_progress(user_id, progress)
            
            # Clear cache
            self.progress_cache.clear()
            
            logger.info("[ProgressTracker] Progress tracker shutdown complete")
            
        except Exception as e:
            logger.error(f"[ProgressTracker] Error during shutdown: {e}")
    
    async def update_progress(
        self,
        user_id: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user progress with new data.
        
        Args:
            user_id: User identifier
            progress_data: New progress data to record
            
        Returns:
            Dictionary with updated progress information
        """
        logger.debug(f"[ProgressTracker] Updating progress for user: {user_id[:8]}...")
        
        try:
            # Load existing progress or create new
            progress = await self._load_progress(user_id)
            if not progress:
                progress = await self._create_initial_progress(user_id)
            
            # Update progress metrics
            await self._update_metrics(progress, progress_data)
            
            # Check for new achievements
            new_achievements = await self._check_achievements(progress, progress_data)
            
            # Update streaks
            await self._update_streaks(progress, progress_data)
            
            # Calculate progress percentages
            await self._calculate_progress_percentages(progress)
            
            # Update timestamp
            progress["last_updated"] = datetime.now().isoformat()
            
            # Save updated progress
            await self._save_progress(user_id, progress)
            self.progress_cache[user_id] = progress
            
            result = {
                "progress": progress,
                "new_achievements": new_achievements,
                "level_up": progress.get("level_changed", False)
            }
            
            logger.debug(f"[ProgressTracker] Updated progress for user: {user_id[:8]}...")
            
            return result
            
        except Exception as e:
            logger.error(f"[ProgressTracker] Failed to update progress for {user_id[:8]}...: {e}")
            return {}
    
    async def get_progress_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of user's current progress.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with progress summary
        """
        try:
            progress = await self._load_progress(user_id)
            if not progress:
                return {}
            
            summary = {
                "current_level": progress.get("current_level", 1),
                "total_points": progress.get("total_points", 0),
                "scenarios_completed": progress.get("scenarios_completed", 0),
                "success_rate": progress.get("overall_success_rate", 0.0),
                "current_streak": progress.get("current_streak", 0),
                "achievements_earned": len(progress.get("achievements", [])),
                "progress_percentages": progress.get("progress_percentages", {}),
                "recent_achievements": progress.get("achievements", [])[-3:],  # Last 3 achievements
                "next_milestones": await self._get_next_milestones(progress)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"[ProgressTracker] Failed to get progress summary: {e}")
            return {}
    
    async def get_leaderboard_data(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's position and nearby users for leaderboard display.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with leaderboard data
        """
        try:
            # This would typically query a database for nearby users
            # For now, return mock data for demonstration
            
            user_progress = await self._load_progress(user_id)
            if not user_progress:
                return {}
            
            user_points = user_progress.get("total_points", 0)
            
            # Mock leaderboard data
            leaderboard = {
                "user_rank": 42,  # Mock rank
                "user_points": user_points,
                "nearby_users": [
                    {"rank": 40, "name": "Anonymous User", "points": user_points + 150},
                    {"rank": 41, "name": "Anonymous User", "points": user_points + 75},
                    {"rank": 42, "name": "You", "points": user_points},
                    {"rank": 43, "name": "Anonymous User", "points": max(0, user_points - 50)},
                    {"rank": 44, "name": "Anonymous User", "points": max(0, user_points - 120)}
                ],
                "top_3": [
                    {"rank": 1, "name": "Security Champion", "points": user_points + 2000},
                    {"rank": 2, "name": "Threat Hunter", "points": user_points + 1800},
                    {"rank": 3, "name": "Cyber Guardian", "points": user_points + 1500}
                ]
            }
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"[ProgressTracker] Failed to get leaderboard data: {e}")
            return {}
    
    # Progress Management Methods
    
    async def _create_initial_progress(self, user_id: str) -> Dict[str, Any]:
        """Create initial progress structure for new user."""
        progress = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "current_level": 1,
            "total_points": 0,
            "scenarios_completed": 0,
            "threats_identified": 0,
            "threats_missed": 0,
            "false_positives": 0,
            "overall_success_rate": 0.0,
            "current_streak": 0,
            "best_streak": 0,
            "achievements": [],
            "milestones": {
                "scenarios": [],
                "success_rates": [],
                "streaks": []
            },
            "progress_percentages": {
                "basic_awareness": 0.0,
                "threat_identification": 0.0,
                "advanced_detection": 0.0,
                "security_mastery": 0.0
            },
            "weekly_stats": {
                "scenarios_this_week": 0,
                "success_rate_this_week": 0.0,
                "week_start": datetime.now().isoformat()
            },
            "session_history": []
        }
        
        return progress
    
    async def _update_metrics(self, progress: Dict[str, Any], progress_data: Dict[str, Any]) -> None:
        """Update progress metrics with new data."""
        # Update basic counters
        if progress_data.get("scenario_completed"):
            progress["scenarios_completed"] += 1
        
        if progress_data.get("threat_identified"):
            progress["threats_identified"] += 1
        elif progress_data.get("threat_missed"):
            progress["threats_missed"] += 1
        
        if progress_data.get("false_positive"):
            progress["false_positives"] += 1
        
        # Update success rate
        total_attempts = progress["threats_identified"] + progress["threats_missed"]
        if total_attempts > 0:
            progress["overall_success_rate"] = progress["threats_identified"] / total_attempts
        
        # Update weekly stats
        await self._update_weekly_stats(progress, progress_data)
        
        # Add to session history
        session_entry = {
            "timestamp": datetime.now().isoformat(),
            "scenario_type": progress_data.get("scenario_type", "unknown"),
            "success": progress_data.get("threat_identified", False),
            "response_time": progress_data.get("response_time", 0),
            "difficulty": progress_data.get("difficulty", 1)
        }
        
        progress["session_history"].append(session_entry)
        
        # Keep only last 50 sessions
        progress["session_history"] = progress["session_history"][-50:]
    
    async def _check_achievements(
        self, 
        progress: Dict[str, Any], 
        progress_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for new achievements and award them."""
        new_achievements = []
        existing_achievement_ids = [a.get("achievement_id") for a in progress.get("achievements", [])]
        
        # First threat identified
        if "first_threat_identified" not in existing_achievement_ids and progress["threats_identified"] >= 1:
            achievement = await self._award_achievement(progress, "first_threat_identified")
            new_achievements.append(achievement)
        
        # Streak achievements
        current_streak = progress.get("current_streak", 0)
        for streak_level in [3, 5, 10]:
            achievement_id = f"streak_{streak_level}"
            if achievement_id not in existing_achievement_ids and current_streak >= streak_level:
                achievement = await self._award_achievement(progress, achievement_id)
                new_achievements.append(achievement)
        
        # Success rate achievements
        success_rate = progress.get("overall_success_rate", 0.0)
        if "phishing_master" not in existing_achievement_ids and success_rate >= 0.9 and progress["scenarios_completed"] >= 10:
            achievement = await self._award_achievement(progress, "phishing_master")
            new_achievements.append(achievement)
        
        # Response time achievements
        if progress["session_history"]:
            recent_sessions = progress["session_history"][-10:]  # Last 10 sessions
            response_times = [s.get("response_time", 0) for s in recent_sessions if s.get("response_time", 0) > 0]
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                
                if "speed_demon" not in existing_achievement_ids and avg_response_time <= 15:
                    achievement = await self._award_achievement(progress, "speed_demon")
                    new_achievements.append(achievement)
                
                elif "thorough_analyzer" not in existing_achievement_ids and avg_response_time >= 60:
                    achievement = await self._award_achievement(progress, "thorough_analyzer")
                    new_achievements.append(achievement)
        
        # Milestone achievements
        scenarios_completed = progress.get("scenarios_completed", 0)
        for milestone in [10, 50, 100]:
            achievement_id = f"milestone_{milestone}"
            if achievement_id not in existing_achievement_ids and scenarios_completed >= milestone:
                achievement = await self._award_achievement(progress, achievement_id)
                new_achievements.append(achievement)
        
        return new_achievements
    
    async def _award_achievement(
        self, 
        progress: Dict[str, Any], 
        achievement_id: str
    ) -> Dict[str, Any]:
        """Award an achievement to the user."""
        achievement_def = self.achievements.get(achievement_id, {})
        
        achievement = {
            "achievement_id": achievement_id,
            "name": achievement_def.get("name", "Unknown Achievement"),
            "description": achievement_def.get("description", "Achievement unlocked!"),
            "points": achievement_def.get("points", 0),
            "earned_at": datetime.now().isoformat()
        }
        
        # Add to user's achievements
        if "achievements" not in progress:
            progress["achievements"] = []
        progress["achievements"].append(achievement)
        
        # Add points
        progress["total_points"] = progress.get("total_points", 0) + achievement["points"]
        
        # Check for level up
        await self._check_level_up(progress)
        
        logger.info(f"[ProgressTracker] Achievement unlocked: {achievement['name']}")
        return achievement
    
    async def _update_streaks(self, progress: Dict[str, Any], progress_data: Dict[str, Any]) -> None:
        """Update user's current and best streaks."""
        if progress_data.get("threat_identified"):
            # Correct identification - increment streak
            progress["current_streak"] = progress.get("current_streak", 0) + 1
            
            # Update best streak if current is higher
            if progress["current_streak"] > progress.get("best_streak", 0):
                progress["best_streak"] = progress["current_streak"]
                
        elif progress_data.get("threat_missed") or progress_data.get("false_positive"):
            # Incorrect - reset streak
            progress["current_streak"] = 0
    
    async def _calculate_progress_percentages(self, progress: Dict[str, Any]) -> None:
        """Calculate progress percentages for different skill areas."""
        scenarios_completed = progress.get("scenarios_completed", 0)
        success_rate = progress.get("overall_success_rate", 0.0)
        
        # Basic awareness (first 10 scenarios, any success rate)
        basic_progress = min(100.0, (scenarios_completed / 10) * 100)
        progress["progress_percentages"]["basic_awareness"] = basic_progress
        
        # Threat identification (10+ scenarios, 70%+ success rate)
        if scenarios_completed >= 10:
            threat_progress = min(100.0, (success_rate / 0.7) * 100)
        else:
            threat_progress = 0.0
        progress["progress_percentages"]["threat_identification"] = threat_progress
        
        # Advanced detection (25+ scenarios, 85%+ success rate)
        if scenarios_completed >= 25:
            advanced_progress = min(100.0, (success_rate / 0.85) * 100)
        else:
            advanced_progress = 0.0
        progress["progress_percentages"]["advanced_detection"] = advanced_progress
        
        # Security mastery (50+ scenarios, 95%+ success rate)
        if scenarios_completed >= 50:
            mastery_progress = min(100.0, (success_rate / 0.95) * 100)
        else:
            mastery_progress = 0.0
        progress["progress_percentages"]["security_mastery"] = mastery_progress
    
    async def _check_level_up(self, progress: Dict[str, Any]) -> None:
        """Check if user has leveled up based on points."""
        total_points = progress.get("total_points", 0)
        current_level = progress.get("current_level", 1)
        
        # Level thresholds (points needed for each level)
        level_thresholds = [0, 50, 150, 300, 500, 750, 1000, 1500, 2000, 2500, 3000]
        
        new_level = current_level
        for level, threshold in enumerate(level_thresholds[1:], 1):
            if total_points >= threshold:
                new_level = level + 1
            else:
                break
        
        if new_level > current_level:
            progress["current_level"] = new_level
            progress["level_changed"] = True
            logger.info(f"[ProgressTracker] User leveled up to level {new_level}!")
        else:
            progress["level_changed"] = False
    
    async def _update_weekly_stats(self, progress: Dict[str, Any], progress_data: Dict[str, Any]) -> None:
        """Update weekly statistics."""
        weekly_stats = progress.get("weekly_stats", {})
        
        # Check if we need to reset weekly stats (new week)
        try:
            week_start = datetime.fromisoformat(weekly_stats.get("week_start", datetime.now().isoformat()))
            if datetime.now() - week_start > timedelta(days=7):
                # Reset weekly stats
                weekly_stats = {
                    "scenarios_this_week": 0,
                    "success_rate_this_week": 0.0,
                    "week_start": datetime.now().isoformat(),
                    "threats_identified_this_week": 0,
                    "threats_missed_this_week": 0
                }
        except:
            # Invalid date, reset
            weekly_stats = {
                "scenarios_this_week": 0,
                "success_rate_this_week": 0.0,
                "week_start": datetime.now().isoformat(),
                "threats_identified_this_week": 0,
                "threats_missed_this_week": 0
            }
        
        # Update weekly counters
        if progress_data.get("scenario_completed"):
            weekly_stats["scenarios_this_week"] += 1
        
        if progress_data.get("threat_identified"):
            weekly_stats["threats_identified_this_week"] = weekly_stats.get("threats_identified_this_week", 0) + 1
        elif progress_data.get("threat_missed"):
            weekly_stats["threats_missed_this_week"] = weekly_stats.get("threats_missed_this_week", 0) + 1
        
        # Update weekly success rate
        weekly_total = weekly_stats.get("threats_identified_this_week", 0) + weekly_stats.get("threats_missed_this_week", 0)
        if weekly_total > 0:
            weekly_stats["success_rate_this_week"] = weekly_stats.get("threats_identified_this_week", 0) / weekly_total
        
        progress["weekly_stats"] = weekly_stats
    
    async def _get_next_milestones(self, progress: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get the next milestones for the user to work towards."""
        milestones = []
        
        scenarios_completed = progress.get("scenarios_completed", 0)
        current_streak = progress.get("current_streak", 0)
        success_rate = progress.get("overall_success_rate", 0.0)
        total_points = progress.get("total_points", 0)
        
        # Scenario milestones
        scenario_milestones = [10, 25, 50, 100, 200]
        for milestone in scenario_milestones:
            if scenarios_completed < milestone:
                milestones.append({
                    "type": "scenarios",
                    "target": milestone,
                    "current": scenarios_completed,
                    "description": f"Complete {milestone} scenarios",
                    "progress_percent": (scenarios_completed / milestone) * 100
                })
                break
        
        # Streak milestones
        streak_milestones = [3, 5, 10, 15, 20]
        for milestone in streak_milestones:
            if current_streak < milestone:
                milestones.append({
                    "type": "streak",
                    "target": milestone,
                    "current": current_streak,
                    "description": f"Achieve a {milestone} threat identification streak",
                    "progress_percent": (current_streak / milestone) * 100
                })
                break
        
        # Success rate milestones
        if scenarios_completed >= 5:  # Only show after enough data
            rate_milestones = [0.7, 0.8, 0.9, 0.95]
            for milestone in rate_milestones:
                if success_rate < milestone:
                    milestones.append({
                        "type": "success_rate",
                        "target": f"{milestone*100:.0f}%",
                        "current": f"{success_rate*100:.1f}%",
                        "description": f"Achieve {milestone*100:.0f}% success rate",
                        "progress_percent": (success_rate / milestone) * 100
                    })
                    break
        
        return milestones[:3]  # Return top 3 next milestones
    
    # Storage Methods
    
    async def _load_progress(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Load user progress from storage."""
        try:
            # Check cache first
            if user_id in self.progress_cache:
                return self.progress_cache[user_id]
            
            # Load from file
            progress_file = self.progress_path / f"{user_id}_progress.json"
            
            if not progress_file.exists():
                return None
            
            with open(progress_file, 'r') as f:
                progress = json.load(f)
            
            # Cache for future use
            self.progress_cache[user_id] = progress
            
            return progress
            
        except Exception as e:
            logger.error(f"[ProgressTracker] Failed to load progress for {user_id[:8]}...: {e}")
            return None
    
    async def _save_progress(self, user_id: str, progress: Dict[str, Any]) -> None:
        """Save user progress to storage."""
        try:
            progress_file = self.progress_path / f"{user_id}_progress.json"
            
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"[ProgressTracker] Failed to save progress for {user_id[:8]}...: {e}")
            raise
    
    async def _load_recent_progress(self) -> None:
        """Load recent progress data into cache."""
        try:
            # Load progress accessed in last 24 hours
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for progress_file in self.progress_path.glob("*_progress.json"):
                if progress_file.stat().st_mtime > cutoff_time.timestamp():
                    user_id = progress_file.stem.replace("_progress", "")
                    progress = await self._load_progress(user_id)
                    if progress:
                        self.progress_cache[user_id] = progress
            
            logger.debug(f"[ProgressTracker] Loaded {len(self.progress_cache)} recent progress records into cache")
            
        except Exception as e:
            logger.warning(f"[ProgressTracker] Failed to load recent progress: {e}")