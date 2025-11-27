#!/usr/bin/env python3
"""
Session Manager Tool - CyberGuard Academy

Handles persistent storage and retrieval of user sessions,
including session state, conversation history, and progress tracking.

Key Features:
- Session persistence to local storage/database
- Session state management and recovery
- Conversation history tracking
- Session timeout and cleanup
- Concurrent session handling
"""

import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger

from cyberguard.models import CyberGuardSession, UserRole, DifficultyLevel, ThreatType, DecisionPoint
from cyberguard.config import Settings


class SessionManager:
    """
    Manages persistent session storage and retrieval.
    
    Handles session lifecycle, persistence, and recovery operations
    for CyberGuard Academy training sessions.
    """
    
    def __init__(self):
        self.settings = Settings()
        self.storage_path = Path("data/sessions")
        self.active_sessions: Dict[str, str] = {}  # session_id -> file_path
        self.session_timeout = timedelta(minutes=self.settings.session_timeout_minutes)
        
        logger.info("[SessionManager] Session manager created")
    
    async def initialize(self) -> None:
        """
        Initialize session storage and load existing sessions.
        """
        logger.info("[SessionManager] Initializing session manager...")
        
        try:
            # Create storage directory
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Reset active sessions registry on startup
            # Since we don't support session resumption yet, we start fresh
            self.active_sessions = {}
            await self._save_active_sessions_registry()
            
            logger.info("[SessionManager] Reset active sessions registry on startup")
            
            logger.info("[SessionManager] Session manager initialized")
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to initialize: {e}")
            raise
    
    async def shutdown(self) -> None:
        """
        Shutdown session manager and save active sessions registry.
        """
        logger.info("[SessionManager] Shutting down session manager...")
        
        try:
            # Save active sessions registry
            await self._save_active_sessions_registry()
            
            logger.info("[SessionManager] Session manager shutdown complete")
            
        except Exception as e:
            logger.error(f"[SessionManager] Error during shutdown: {e}")
    
    async def save_session(self, session: CyberGuardSession) -> bool:
        """
        Save session to persistent storage.
        
        Args:
            session: CyberGuardSession to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Generate file path
            session_file = self.storage_path / f"{session.session_id}.json"
            
            # Convert session to dict for JSON serialization
            session_data = {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "user_role": session.user_role.value if hasattr(session.user_role, 'value') else session.user_role,
                "current_difficulty": session.current_difficulty.value if hasattr(session.current_difficulty, 'value') else session.current_difficulty,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "scenario_type": session.scenario_type.value if hasattr(session.scenario_type, 'value') else session.scenario_type,
                "scenario_id": session.scenario_id,
                "current_state": session.current_state,
                "conversation_history": session.conversation_history,
                "decision_points": [dp.dict() if hasattr(dp, 'dict') else dp for dp in session.decision_points],
                "threat_actor_active": session.threat_actor_active,
                "hints_used": session.hints_used,
                "pause_count": session.pause_count,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            }
            
            # Write to file
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            # Update active sessions registry
            if session.end_time is None:  # Session is active if not ended
                self.active_sessions[session.session_id] = str(session_file)
            elif session.session_id in self.active_sessions:
                del self.active_sessions[session.session_id]
            
            logger.debug(f"[SessionManager] Saved session: {session.session_id[:8]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to save session {session.session_id[:8]}...: {e}")
            return False
    
    async def load_session(self, session_id: str) -> Optional[CyberGuardSession]:
        """
        Load session from persistent storage.
        
        Args:
            session_id: ID of session to load
            
        Returns:
            CyberGuardSession if found, None otherwise
        """
        try:
            # Find session file
            session_file = self.storage_path / f"{session_id}.json"
            
            if not session_file.exists():
                logger.debug(f"[SessionManager] Session file not found: {session_id[:8]}...")
                return None
            
            # Load session data
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            
            # Convert back to CyberGuardSession object
            session = CyberGuardSession(
                session_id=session_data["session_id"],
                user_id=session_data["user_id"],
                user_role=UserRole(session_data["user_role"]),
                scenario_type=ThreatType(session_data["scenario_type"]),
                scenario_id=session_data["scenario_id"],
                current_difficulty=DifficultyLevel(session_data["current_difficulty"]),
                current_state=session_data.get("current_state", "intro"),
                start_time=session_data.get("start_time", datetime.now().timestamp()),
                end_time=session_data.get("end_time"),
                conversation_history=session_data.get("conversation_history", []),
                decision_points=session_data.get("decision_points", []),
                threat_actor_active=session_data.get("threat_actor_active"),
                hints_used=session_data.get("hints_used", 0),
                pause_count=session_data.get("pause_count", 0),
                created_at=datetime.fromisoformat(session_data["created_at"]),
                updated_at=datetime.fromisoformat(session_data["updated_at"])
            )
            
            logger.debug(f"[SessionManager] Loaded session: {session_id[:8]}...")
            return session
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to load session {session_id[:8]}...: {e}")
            return None
    
    async def get_active_session_ids(self) -> List[str]:
        """
        Get list of all active session IDs.
        
        Returns:
            List of active session IDs
        """
        return list(self.active_sessions.keys())
    
    async def deactivate_session(self, session_id: str) -> bool:
        """
        Mark session as inactive and update storage.
        
        Args:
            session_id: ID of session to deactivate
            
        Returns:
            bool: True if deactivated successfully
        """
        try:
            # Load session
            session = await self.load_session(session_id)
            if not session:
                return False
            
            # Mark as inactive
            session.is_active = False
            session.last_activity = datetime.now()
            
            # Save updated session
            success = await self.save_session(session)
            
            if success:
                logger.info(f"[SessionManager] Deactivated session: {session_id[:8]}...")
            
            return success
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to deactivate session {session_id[:8]}...: {e}")
            return False
    
    async def cleanup_old_sessions(self, days_old: int = 7) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Remove sessions older than this many days
            
        Returns:
            int: Number of sessions cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_count = 0
            
            # Check all session files
            for session_file in self.storage_path.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    updated_at = session_data.get("updated_at")
                    if updated_at:
                        activity_date = datetime.fromisoformat(updated_at)
                    else:
                        activity_date = datetime.fromtimestamp(session_data.get("start_time", datetime.now().timestamp()))
                    
                    if activity_date < cutoff_date:
                        # Remove file and from active sessions
                        session_id = session_data["session_id"]
                        session_file.unlink()
                        
                        if session_id in self.active_sessions:
                            del self.active_sessions[session_id]
                        
                        cleaned_count += 1
                        logger.debug(f"[SessionManager] Cleaned up old session: {session_id[:8]}...")
                
                except Exception as e:
                    logger.warning(f"[SessionManager] Error processing session file {session_file}: {e}")
                    continue
            
            if cleaned_count > 0:
                logger.info(f"[SessionManager] Cleaned up {cleaned_count} old sessions")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to cleanup old sessions: {e}")
            return 0
    
    async def get_user_sessions(self, user_id: str, active_only: bool = True) -> List[str]:
        """
        Get all session IDs for a specific user.
        
        Args:
            user_id: User ID to search for
            active_only: If True, only return active sessions
            
        Returns:
            List of session IDs for the user
        """
        try:
            user_sessions = []
            
            # Check all session files
            for session_file in self.storage_path.glob("*.json"):
                try:
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    if session_data.get("user_id") == user_id:
                        if not active_only or session_data.get("is_active", False):
                            user_sessions.append(session_data["session_id"])
                
                except Exception as e:
                    logger.warning(f"[SessionManager] Error reading session file {session_file}: {e}")
                    continue
            
            return user_sessions
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to get user sessions: {e}")
            return []
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current session storage.
        
        Returns:
            Dictionary with session statistics
        """
        try:
            total_sessions = 0
            active_sessions = 0
            total_size = 0
            
            for session_file in self.storage_path.glob("*.json"):
                try:
                    total_sessions += 1
                    total_size += session_file.stat().st_size
                    
                    with open(session_file, 'r') as f:
                        session_data = json.load(f)
                    
                    if session_data.get("is_active", False):
                        active_sessions += 1
                
                except Exception as e:
                    logger.warning(f"[SessionManager] Error reading session file {session_file}: {e}")
                    continue
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "inactive_sessions": total_sessions - active_sessions,
                "storage_size_bytes": total_size,
                "storage_path": str(self.storage_path)
            }
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to get session stats: {e}")
            return {}
    
    # Private Helper Methods
    
    async def _load_active_sessions_registry(self) -> None:
        """Load the active sessions registry from file."""
        try:
            registry_file = self.storage_path / "active_sessions.json"
            
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    self.active_sessions = json.load(f)
                
                logger.debug(f"[SessionManager] Loaded {len(self.active_sessions)} active sessions from registry")
            
        except Exception as e:
            logger.warning(f"[SessionManager] Failed to load active sessions registry: {e}")
            self.active_sessions = {}
    
    async def _save_active_sessions_registry(self) -> None:
        """Save the active sessions registry to file."""
        try:
            registry_file = self.storage_path / "active_sessions.json"
            
            with open(registry_file, 'w') as f:
                json.dump(self.active_sessions, f, indent=2)
            
            logger.debug(f"[SessionManager] Saved {len(self.active_sessions)} active sessions to registry")
            
        except Exception as e:
            logger.error(f"[SessionManager] Failed to save active sessions registry: {e}")
    
    async def _cleanup_expired_sessions(self) -> None:
        """Clean up expired sessions based on timeout."""
        try:
            expired_sessions = []
            current_time = datetime.now(timezone.utc)
            
            for session_id in list(self.active_sessions.keys()):
                session = await self.load_session(session_id)
                if session:
                    last_activity = session.updated_at
                    if current_time - last_activity > self.session_timeout:
                        expired_sessions.append(session_id)
            
            # Deactivate expired sessions
            for session_id in expired_sessions:
                await self.deactivate_session(session_id)
            
            if expired_sessions:
                logger.info(f"[SessionManager] Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"[SessionManager] Failed to cleanup expired sessions: {e}")