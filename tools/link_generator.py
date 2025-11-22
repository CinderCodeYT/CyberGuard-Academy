"""
Link Generator Tool - Safe phishing link generation for training scenarios.

Generates realistic but safe phishing links for training purposes:
1. Creates convincing URLs that redirect to safe educational content
2. Uses domain spoofing techniques for educational demonstration
3. Embeds tracking parameters for evaluation analytics
4. Ensures all links redirect to safe training environment
5. Never creates actual malicious functionality

Key principle: Links should demonstrate real attack patterns
while maintaining complete safety through controlled redirection.
"""

from typing import Dict, Any, List
from urllib.parse import urlencode
import uuid

from cyberguard.models import SocialEngineeringPattern, DifficultyLevel, UserRole
from cyberguard.config import settings


class LinkGenerator:
    """
    Safe phishing link generation for training scenarios.
    
    Creates realistic but safe URLs that demonstrate real attack patterns
    while redirecting to educational content in the training environment.
    """

    def __init__(self):
        self.link_templates = {}
        self.generated_links = {}
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize link templates and tracking."""
        print("[LinkGenerator] Loading link templates...")
        
        # Load domain spoofing templates
        self.link_templates = self._load_link_templates()
        
        self.is_initialized = True
        print("[LinkGenerator] Link generator initialized")

    async def shutdown(self) -> None:
        """Clean up resources."""
        print("[LinkGenerator] Link generator shutting down")
        self.link_templates.clear()
        self.generated_links.clear()
        self.is_initialized = False

    async def generate_phishing_link(
        self,
        threat_pattern: SocialEngineeringPattern,
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        scenario_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a safe phishing link for training.
        
        Args:
            threat_pattern: Social engineering pattern being used
            user_role: Target user's job function
            difficulty_level: Sophistication level of the link
            scenario_context: Additional context for customization
            
        Returns:
            Generated link with metadata for evaluation
        """
        print(f"[LinkGenerator] Generating {threat_pattern.value} link for {user_role.value}")
        
        # Select appropriate link template
        template = self._select_link_template(threat_pattern, user_role, difficulty_level)
        
        # Generate link components
        domain = self._generate_spoofed_domain(template, difficulty_level)
        path = self._generate_path(template, threat_pattern)
        parameters = self._generate_parameters(template, scenario_context)
        
        # Build final URL
        full_url = self._build_url(domain, path, parameters)
        
        # Generate safe redirect URL
        safe_redirect = self._create_safe_redirect(full_url, scenario_context)
        
        # Identify red flags for educational purposes
        red_flags = self._identify_link_red_flags(domain, path, parameters, difficulty_level)
        
        link_data = {
            "display_url": full_url,  # What user sees
            "actual_url": safe_redirect,  # Where it actually goes (safe)
            "domain": domain,
            "path": path,
            "parameters": parameters,
            "red_flags": red_flags,
            "metadata": {
                "pattern": threat_pattern.value,
                "difficulty": difficulty_level.value,
                "target_role": user_role.value,
                "spoofing_techniques": template.get("spoofing_techniques", [])
            }
        }
        
        # Track generated link
        self._track_link_generation(link_data, scenario_context)
        
        return link_data
    
    def _load_link_templates(self) -> Dict[str, Any]:
        """Load link spoofing templates."""
        return {
            "banking_spoofs": {
                "legitimate_domains": ["bankofamerica.com", "chase.com", "wellsfargo.com"],
                "spoofing_techniques": ["character_substitution", "subdomain_spoofing", "domain_extension"],
                "common_paths": ["/login", "/security", "/verify", "/account"]
            },
            "tech_company_spoofs": {
                "legitimate_domains": ["microsoft.com", "google.com", "apple.com"],
                "spoofing_techniques": ["homograph_attack", "subdomain_spoofing", "typosquatting"],
                "common_paths": ["/signin", "/security", "/account", "/support"]
            },
            "social_media_spoofs": {
                "legitimate_domains": ["facebook.com", "linkedin.com", "twitter.com"],
                "spoofing_techniques": ["character_substitution", "domain_extension"],
                "common_paths": ["/login", "/security", "/settings", "/verify"]
            },
            "company_spoofs": {
                "legitimate_domains": ["company.com", "yourcompany.com", "corporate.com"],
                "spoofing_techniques": ["subdomain_spoofing", "domain_variation"],
                "common_paths": ["/portal", "/hr", "/it", "/security"]
            }
        }
    
    def _select_link_template(
        self,
        pattern: SocialEngineeringPattern,
        role: UserRole,
        difficulty: DifficultyLevel
    ) -> Dict[str, Any]:
        """Select appropriate link template based on context."""
        
        # Map user roles to relevant spoofing categories
        role_template_map = {
            UserRole.FINANCE: "banking_spoofs",
            UserRole.IT_ADMIN: "tech_company_spoofs", 
            UserRole.HR: "company_spoofs",
            UserRole.MANAGER: "company_spoofs",
            UserRole.GENERAL: "tech_company_spoofs"
        }
        
        template_category = role_template_map.get(role, "tech_company_spoofs")
        return self.link_templates.get(template_category, self.link_templates["tech_company_spoofs"])
    
    def _generate_spoofed_domain(self, template: Dict[str, Any], difficulty: DifficultyLevel) -> str:
        """Generate spoofed domain based on difficulty level."""
        
        legitimate_domains = template.get("legitimate_domains", ["microsoft.com"])
        spoofing_techniques = template.get("spoofing_techniques", ["character_substitution"])
        
        import random
        base_domain = random.choice(legitimate_domains)
        technique = random.choice(spoofing_techniques)
        
        if difficulty == DifficultyLevel.BEGINNER:
            # Obvious spoofing for easier detection
            return self._apply_obvious_spoofing(base_domain)
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # Moderate spoofing
            return self._apply_moderate_spoofing(base_domain, technique)
        else:
            # Sophisticated spoofing
            return self._apply_sophisticated_spoofing(base_domain, technique)
    
    def _apply_obvious_spoofing(self, domain: str) -> str:
        """Apply obvious domain spoofing for beginner difficulty."""
        techniques = [
            f"fake-{domain}",
            f"{domain}.security-alert.net",
            domain.replace(".com", ".net"),
            domain.replace("o", "0").replace("e", "3")  # Character substitution
        ]
        
        import random
        return random.choice(techniques)
    
    def _apply_moderate_spoofing(self, domain: str, technique: str) -> str:
        """Apply moderate domain spoofing."""
        if technique == "character_substitution":
            # Subtle character substitution
            substitutions = {"rn": "m", "cl": "d", "vv": "w"}
            for old, new in substitutions.items():
                if old in domain:
                    return domain.replace(old, new)
        
        elif technique == "subdomain_spoofing":
            return f"security.{domain}.verify-account.net"
        
        elif technique == "domain_extension":
            return domain.replace(".com", ".co") 
        
        # Fallback
        return f"secure-{domain}"
    
    def _apply_sophisticated_spoofing(self, domain: str, technique: str) -> str:
        """Apply sophisticated domain spoofing for advanced users."""
        if technique == "homograph_attack":
            # Use similar-looking characters (simplified for demo)
            return domain.replace("o", "о").replace("a", "а")  # Cyrillic characters
        
        elif technique == "subdomain_spoofing":
            # Legitimate-looking subdomain
            return f"portal.{domain.split('.')[0]}-security.com"
        
        # Fallback to moderate spoofing
        return self._apply_moderate_spoofing(domain, technique)
    
    def _generate_path(self, template: Dict[str, Any], pattern: SocialEngineeringPattern) -> str:
        """Generate URL path based on social engineering pattern."""
        
        common_paths = template.get("common_paths", ["/login"])
        
        pattern_paths = {
            SocialEngineeringPattern.URGENCY: ["/urgent-verify", "/security-alert", "/immediate-action"],
            SocialEngineeringPattern.AUTHORITY: ["/admin-required", "/policy-update", "/compliance"],
            SocialEngineeringPattern.CURIOSITY: ["/confidential", "/bonus-info", "/exclusive"]
        }
        
        # Combine common paths with pattern-specific paths
        available_paths = common_paths + pattern_paths.get(pattern, [])
        
        import random
        return random.choice(available_paths)
    
    def _generate_parameters(self, template: Dict[str, Any], scenario_context: Dict[str, Any]) -> Dict[str, str]:
        """Generate URL parameters for tracking and realism."""
        
        params = {
            "token": str(uuid.uuid4())[:16],  # Realistic token
            "ref": "email",
            "utm_source": "security_alert"
        }
        
        # Add session-specific parameters if available
        if scenario_context:
            session_id = scenario_context.get("session_id")
            if session_id:
                params["session"] = session_id[:8]  # Truncated for realism
        
        return params
    
    def _build_url(self, domain: str, path: str, parameters: Dict[str, str]) -> str:
        """Build the complete URL."""
        base_url = f"https://{domain}{path}"
        
        if parameters:
            query_string = urlencode(parameters)
            return f"{base_url}?{query_string}"
        
        return base_url
    
    def _create_safe_redirect(self, spoofed_url: str, scenario_context: Dict[str, Any]) -> str:
        """Create safe redirect URL for the spoofed link."""
        
        # Generate unique redirect ID
        redirect_id = str(uuid.uuid4())
        
        # Store the mapping (in production, this would be in a database)
        self.generated_links[redirect_id] = {
            "spoofed_url": spoofed_url,
            "scenario_context": scenario_context,
            "created_at": str(uuid.uuid4())  # Placeholder timestamp
        }
        
        # Return safe redirect URL
        return f"{settings.safe_redirect_base_url}?redirect_id={redirect_id}&type=phishing_training"
    
    def _identify_link_red_flags(
        self,
        domain: str,
        path: str,
        parameters: Dict[str, str],
        difficulty: DifficultyLevel
    ) -> List[Dict[str, Any]]:
        """Identify red flags in the generated link for educational purposes."""
        
        red_flags = []
        
        # Domain red flags
        if any(char in domain for char in ["0", "3", "-", "fake"]):
            red_flags.append({
                "type": "suspicious_domain",
                "description": "Domain contains suspicious characters or keywords",
                "severity": "high",
                "location": "domain_name"
            })
        
        if domain.count(".") > 2:
            red_flags.append({
                "type": "excessive_subdomains",
                "description": "Unusually complex domain structure",
                "severity": "medium",
                "location": "domain_structure"
            })
        
        # Path red flags
        if any(word in path.lower() for word in ["urgent", "immediate", "verify", "security"]):
            red_flags.append({
                "type": "urgent_path",
                "description": "URL path suggests urgency or security concerns",
                "severity": "medium",
                "location": "url_path"
            })
        
        # Parameter red flags
        if "token" in parameters and len(parameters["token"]) < 20:
            red_flags.append({
                "type": "short_token",
                "description": "Security token appears too short for legitimate use",
                "severity": "low",
                "location": "url_parameters"
            })
        
        return red_flags
    
    def _track_link_generation(self, link_data: Dict[str, Any], scenario_context: Dict[str, Any]) -> None:
        """Track generated links for analytics."""
        
        session_id = scenario_context.get("session_id", "unknown") if scenario_context else "unknown"
        
        if session_id not in self.generated_links:
            # Create session tracking entry if needed
            pass
        
        print(f"[LinkGenerator] Generated link: {link_data['display_url']}")
        print(f"[LinkGenerator] Red flags: {len(link_data['red_flags'])}")
