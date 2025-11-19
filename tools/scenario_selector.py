"""
Scenario Selector Tool - Intelligent scenario selection for adaptive training.

This tool selects the most appropriate cybersecurity training scenario based on:
1. User role and job function
2. Current difficulty level and performance history  
3. Recently seen patterns (to avoid repetition)
4. Identified vulnerability areas needing focus
5. Threat landscape and current attack trends

The goal is to provide personalized, relevant training that targets 70% success rate.
"""

from typing import Dict, List, Any, Optional
import random
from datetime import datetime

from cyberguard.models import UserRole, DifficultyLevel, ThreatType, SocialEngineeringPattern
from cyberguard.config import settings


class ScenarioSelector:
    """
    Intelligent scenario selection engine for personalized cybersecurity training.
    
    Uses adaptive algorithms to select scenarios that are:
    - Appropriately challenging for the user's skill level
    - Relevant to their job function and responsibilities  
    - Focused on their known vulnerability patterns
    - Varied to prevent pattern memorization
    """
    
    def __init__(self):
        self.scenario_database = {}
        self.selection_history = {}
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize scenario database and selection algorithms."""
        print("[ScenarioSelector] Initializing scenario database...")
        
        # Load scenario templates (in production, this would be from a database)
        self.scenario_database = await self._load_scenario_templates()
        
        # Initialize selection tracking
        self.selection_history = {}
        
        self.is_initialized = True
        print(f"[ScenarioSelector] Loaded {len(self.scenario_database)} scenario templates")

    async def shutdown(self) -> None:
        """Clean up resources."""
        print("[ScenarioSelector] Shutting down scenario selector")
        self.scenario_database.clear()
        self.selection_history.clear()

    async def select_scenario(
        self,
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        threat_type: str,
        recently_seen_patterns: List[str] = None,
        vulnerability_areas: List[str] = None,
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Select optimal scenario for user's current training needs.
        
        Args:
            user_role: User's job function for role-specific scenarios
            difficulty_level: Current adaptive difficulty (1-5)
            threat_type: Type of cybersecurity threat to simulate
            recently_seen_patterns: Patterns to avoid for variety
            vulnerability_areas: User's known weakness areas to focus on
            user_preferences: Additional user customization options
            
        Returns:
            Selected scenario with content templates and metadata
        """
        if not self.is_initialized:
            await self.initialize()
        
        recently_seen = recently_seen_patterns or []
        vulnerabilities = vulnerability_areas or []
        preferences = user_preferences or {}
        
        print(f"[ScenarioSelector] Selecting {threat_type} scenario for {user_role.value}, difficulty {difficulty_level.value}")
        
        # Get candidate scenarios matching basic criteria
        candidates = self._get_candidate_scenarios(
            user_role=user_role,
            difficulty_level=difficulty_level,
            threat_type=threat_type
        )
        
        if not candidates:
            # Fallback to default scenarios
            return self._get_fallback_scenario(threat_type, difficulty_level)
        
        # Score candidates based on selection criteria
        scored_candidates = []
        for scenario in candidates:
            score = self._calculate_scenario_score(
                scenario=scenario,
                user_role=user_role,
                recently_seen_patterns=recently_seen,
                vulnerability_areas=vulnerabilities,
                user_preferences=preferences
            )
            scored_candidates.append((scenario, score))
        
        # Select highest scoring scenario
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        selected_scenario = scored_candidates[0][0]
        
        # Customize scenario for user
        customized_scenario = await self._customize_scenario(
            scenario=selected_scenario,
            user_role=user_role,
            difficulty_level=difficulty_level,
            vulnerability_focus=vulnerabilities
        )
        
        # Track selection for future variety
        self._track_scenario_selection(user_role.value, selected_scenario["id"])
        
        print(f"[ScenarioSelector] Selected scenario: {selected_scenario['title']} (score: {scored_candidates[0][1]:.2f})")
        
        return customized_scenario

    async def _load_scenario_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load scenario templates from database/files."""
        
        # In production, this would load from a database
        # For now, we'll create a representative sample
        
        scenarios = {
            "phishing": [
                {
                    "id": "phishing_urgent_payment",
                    "title": "Urgent Vendor Payment Request", 
                    "description": "CEO requests immediate wire transfer for overdue vendor payment",
                    "difficulty_base": 3,
                    "patterns": ["urgency", "authority"],
                    "target_roles": ["finance", "executive", "manager"],
                    "red_flags": ["external_email", "urgency_language", "financial_request"],
                    "template": "vendor_payment_phishing.json"
                },
                {
                    "id": "phishing_it_credential",
                    "title": "IT Security Alert",
                    "description": "Fake IT department requesting password verification",
                    "difficulty_base": 2,
                    "patterns": ["authority", "fear"],
                    "target_roles": ["developer", "general", "it_admin"],
                    "red_flags": ["password_request", "suspicious_domain", "urgency"],
                    "template": "it_security_phishing.json"
                },
                {
                    "id": "phishing_hr_bonus",
                    "title": "Annual Bonus Information",
                    "description": "HR department sharing bonus details via suspicious link",
                    "difficulty_base": 4,
                    "patterns": ["curiosity", "greed"],
                    "target_roles": ["general", "developer", "manager"],
                    "red_flags": ["suspicious_link", "external_sender", "sensitive_info"],
                    "template": "hr_bonus_phishing.json"
                }
            ],
            "vishing": [
                {
                    "id": "vishing_tech_support",
                    "title": "Tech Support Scam Call",
                    "description": "Fake Microsoft support claiming computer infection",
                    "difficulty_base": 2,
                    "patterns": ["authority", "fear"],
                    "target_roles": ["general", "executive"],
                    "red_flags": ["cold_call", "remote_access_request", "payment_demand"],
                    "template": "tech_support_vishing.json"
                }
            ],
            "bec": [
                {
                    "id": "bec_ceo_fraud",
                    "title": "CEO Wire Transfer Request",
                    "description": "Executive impersonation requesting confidential wire transfer",
                    "difficulty_base": 4,
                    "patterns": ["authority", "urgency"],
                    "target_roles": ["finance", "executive"],
                    "red_flags": ["executive_impersonation", "secrecy_request", "financial_transaction"],
                    "template": "ceo_fraud_bec.json"
                }
            ]
        }
        
        return scenarios

    def _get_candidate_scenarios(
        self,
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        threat_type: str
    ) -> List[Dict[str, Any]]:
        """Get scenarios matching basic filtering criteria."""
        
        if threat_type not in self.scenario_database:
            return []
        
        scenarios = self.scenario_database[threat_type]
        candidates = []
        
        for scenario in scenarios:
            # Check if scenario is appropriate for user role
            if user_role.value in scenario["target_roles"] or "general" in scenario["target_roles"]:
                # Check if difficulty is within reasonable range
                difficulty_range = abs(scenario["difficulty_base"] - difficulty_level.value)
                if difficulty_range <= 2:  # Allow +/-2 difficulty levels
                    candidates.append(scenario)
        
        return candidates

    def _calculate_scenario_score(
        self,
        scenario: Dict[str, Any],
        user_role: UserRole,
        recently_seen_patterns: List[str],
        vulnerability_areas: List[str],
        user_preferences: Dict[str, Any]
    ) -> float:
        """Calculate relevance score for scenario selection."""
        
        score = 0.0
        
        # Base score for role relevance
        if user_role.value in scenario["target_roles"]:
            score += 50.0
        elif "general" in scenario["target_roles"]:
            score += 25.0
        
        # Bonus for targeting user's vulnerability areas
        scenario_patterns = scenario.get("patterns", [])
        for vulnerability in vulnerability_areas:
            if vulnerability in scenario_patterns:
                score += 30.0
        
        # Penalty for recently seen patterns (encourage variety)
        pattern_overlap = set(scenario_patterns) & set(recently_seen_patterns)
        score -= len(pattern_overlap) * 15.0
        
        # Bonus for scenario freshness
        user_key = user_role.value
        if user_key in self.selection_history:
            times_selected = self.selection_history[user_key].get(scenario["id"], 0)
            score -= times_selected * 10.0  # Reduce score for repeated scenarios
        
        # Random factor for variety (small)
        score += random.uniform(-5.0, 5.0)
        
        return max(score, 0.0)  # Ensure non-negative score

    async def _customize_scenario(
        self,
        scenario: Dict[str, Any],
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        vulnerability_focus: List[str]
    ) -> Dict[str, Any]:
        """Customize selected scenario for user's specific context."""
        
        customized = scenario.copy()
        
        # Adjust difficulty based on user level
        difficulty_adjustment = difficulty_level.value - scenario["difficulty_base"]
        customized["adjusted_difficulty"] = difficulty_level.value
        
        # Add role-specific context
        customized["role_context"] = self._get_role_context(user_role)
        
        # Emphasize vulnerability areas
        if vulnerability_focus:
            customized["vulnerability_emphasis"] = vulnerability_focus
        
        # Add difficulty adjustments
        if difficulty_adjustment > 0:
            customized["difficulty_modifiers"] = {
                "more_subtle_red_flags": True,
                "realistic_sender_details": True,
                "time_pressure": True
            }
        elif difficulty_adjustment < 0:
            customized["difficulty_modifiers"] = {
                "obvious_red_flags": True,
                "clear_warnings": True,
                "longer_decision_time": True
            }
        
        # Add selection metadata
        customized["selection_metadata"] = {
            "selected_at": datetime.utcnow().isoformat(),
            "selected_for_user": user_role.value,
            "target_difficulty": difficulty_level.value,
            "customization_applied": True
        }
        
        return customized

    def _get_role_context(self, user_role: UserRole) -> Dict[str, Any]:
        """Get role-specific context for scenario customization."""
        
        role_contexts = {
            UserRole.DEVELOPER: {
                "work_context": "software development team",
                "likely_contacts": ["product_manager", "tech_lead", "devops"],
                "sensitive_areas": ["code_repositories", "api_keys", "deployment_systems"],
                "communication_style": "technical and informal"
            },
            UserRole.FINANCE: {
                "work_context": "financial operations team", 
                "likely_contacts": ["vendors", "executives", "accounting"],
                "sensitive_areas": ["wire_transfers", "financial_data", "vendor_payments"],
                "communication_style": "formal and process-oriented"
            },
            UserRole.EXECUTIVE: {
                "work_context": "senior leadership team",
                "likely_contacts": ["board_members", "direct_reports", "external_partners"],
                "sensitive_areas": ["strategic_information", "m&a_activity", "financial_performance"],
                "communication_style": "high-level and decisive"
            },
            UserRole.HR: {
                "work_context": "human resources department",
                "likely_contacts": ["employees", "managers", "external_recruiters"],
                "sensitive_areas": ["employee_data", "compensation", "hiring_information"], 
                "communication_style": "professional and supportive"
            }
        }
        
        return role_contexts.get(user_role, {
            "work_context": "general office environment",
            "likely_contacts": ["colleagues", "managers", "external_partners"],
            "sensitive_areas": ["company_information", "personal_data"],
            "communication_style": "professional"
        })

    def _get_fallback_scenario(self, threat_type: str, difficulty_level: DifficultyLevel) -> Dict[str, Any]:
        """Return default scenario if no candidates found."""
        
        return {
            "id": f"fallback_{threat_type}",
            "title": f"Basic {threat_type.title()} Scenario",
            "description": f"Generic {threat_type} training scenario",
            "difficulty_base": difficulty_level.value,
            "patterns": ["urgency"],
            "target_roles": ["general"],
            "red_flags": ["suspicious_request"],
            "template": f"basic_{threat_type}.json",
            "is_fallback": True,
            "role_context": self._get_role_context(UserRole.GENERAL),
            "selection_metadata": {
                "selected_at": datetime.utcnow().isoformat(),
                "fallback_reason": "no_matching_candidates",
                "target_difficulty": difficulty_level.value
            }
        }

    def _track_scenario_selection(self, user_role: str, scenario_id: str) -> None:
        """Track scenario selection for variety optimization."""
        
        if user_role not in self.selection_history:
            self.selection_history[user_role] = {}
        
        if scenario_id not in self.selection_history[user_role]:
            self.selection_history[user_role][scenario_id] = 0
        
        self.selection_history[user_role][scenario_id] += 1

    def get_selection_stats(self, user_role: Optional[str] = None) -> Dict[str, Any]:
        """Get selection statistics for monitoring and optimization."""
        
        if user_role:
            return {
                "user_role": user_role,
                "scenarios_selected": self.selection_history.get(user_role, {}),
                "total_selections": sum(self.selection_history.get(user_role, {}).values())
            }
        
        return {
            "total_scenarios_available": sum(len(scenarios) for scenarios in self.scenario_database.values()),
            "selection_history": self.selection_history,
            "most_selected_scenarios": self._get_most_selected_scenarios()
        }

    def _get_most_selected_scenarios(self) -> List[Dict[str, Any]]:
        """Get most frequently selected scenarios across all users."""
        
        scenario_counts = {}
        for role_history in self.selection_history.values():
            for scenario_id, count in role_history.items():
                if scenario_id not in scenario_counts:
                    scenario_counts[scenario_id] = 0
                scenario_counts[scenario_id] += count
        
        # Sort by count and return top 10
        sorted_scenarios = sorted(scenario_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {"scenario_id": scenario_id, "selection_count": count}
            for scenario_id, count in sorted_scenarios[:10]
        ]