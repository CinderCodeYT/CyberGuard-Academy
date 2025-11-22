"""
Header Spoofing Tool - Email header manipulation for training scenarios.

Generates realistic email headers that demonstrate spoofing techniques:
1. Creates convincing sender information with subtle spoofing
2. Demonstrates header-based social engineering techniques
3. Embeds educational red flags in email metadata
4. Ensures all spoofing is for training purposes only
5. Tracks spoofing techniques for evaluation analytics

Key principle: Headers should demonstrate real spoofing patterns
while maintaining clear educational value and safety.
"""

from typing import Dict, Any, List
import uuid
from datetime import datetime, timezone

from cyberguard.models import SocialEngineeringPattern, DifficultyLevel, UserRole


class HeaderSpoofing:
    """
    Email header spoofing for cybersecurity training scenarios.
    
    Creates realistic but safe email headers that demonstrate
    common spoofing techniques used in phishing attacks.
    """

    def __init__(self):
        self.header_templates = {}
        self.spoofing_history = {}
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize header templates and spoofing patterns."""
        print("[HeaderSpoofing] Loading header spoofing templates...")
        
        # Load spoofing templates
        self.header_templates = self._load_header_templates()
        
        self.is_initialized = True
        print("[HeaderSpoofing] Header spoofing initialized")

    async def shutdown(self) -> None:
        """Clean up resources."""
        print("[HeaderSpoofing] Header spoofing shutting down")
        self.header_templates.clear()
        self.spoofing_history.clear()
        self.is_initialized = False

    async def generate_spoofed_headers(
        self,
        sender_info: Dict[str, Any],
        threat_pattern: SocialEngineeringPattern,
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        scenario_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate spoofed email headers for training.
        
        Args:
            sender_info: Basic sender information from email generator
            threat_pattern: Social engineering pattern being used
            user_role: Target user's job function
            difficulty_level: Sophistication level of spoofing
            scenario_context: Additional context for customization
            
        Returns:
            Complete email headers with spoofing and metadata
        """
        print(f"[HeaderSpoofing] Generating headers for {sender_info.get('name', 'Unknown')}")
        
        # Generate core headers
        headers = self._generate_core_headers(sender_info, difficulty_level)
        
        # Add spoofing techniques based on difficulty
        spoofed_headers = self._apply_spoofing_techniques(headers, difficulty_level)
        
        # Add authentication headers (SPF, DKIM, DMARC)
        auth_headers = self._generate_auth_headers(spoofed_headers, difficulty_level)
        
        # Identify red flags for educational purposes
        red_flags = self._identify_header_red_flags(spoofed_headers, auth_headers, difficulty_level)
        
        header_data = {
            "headers": {**spoofed_headers, **auth_headers},
            "red_flags": red_flags,
            "metadata": {
                "spoofing_techniques": self._get_applied_techniques(spoofed_headers, difficulty_level),
                "difficulty": difficulty_level.value,
                "educational_focus": self._get_educational_focus(red_flags)
            }
        }
        
        # Track header generation
        self._track_header_generation(header_data, scenario_context)
        
        return header_data
    
    def _load_header_templates(self) -> Dict[str, Any]:
        """Load header spoofing templates."""
        return {
            "legitimate_domains": {
                "corporate": ["company.com", "corp.com", "enterprise.com"],
                "banking": ["bank.com", "financial.com", "trust.com"],
                "tech": ["tech.com", "software.com", "cloud.com"],
                "government": ["gov.org", "agency.gov", "department.gov"]
            },
            "spoofing_techniques": {
                "display_name_spoofing": {
                    "description": "Legitimate display name with spoofed email",
                    "difficulty": "beginner",
                    "detection_difficulty": "easy"
                },
                "domain_spoofing": {
                    "description": "Similar-looking domain names",
                    "difficulty": "intermediate", 
                    "detection_difficulty": "medium"
                },
                "subdomain_spoofing": {
                    "description": "Legitimate-looking subdomains",
                    "difficulty": "advanced",
                    "detection_difficulty": "hard"
                },
                "reply_to_spoofing": {
                    "description": "Different reply-to address",
                    "difficulty": "intermediate",
                    "detection_difficulty": "medium"
                }
            }
        }
    
    def _generate_core_headers(self, sender_info: Dict[str, Any], difficulty: DifficultyLevel) -> Dict[str, str]:
        """Generate basic email headers."""
        
        # Generate realistic message ID
        message_id = f"<{uuid.uuid4()}@{sender_info.get('email', 'unknown.com').split('@')[1]}>"
        
        # Generate timestamp
        timestamp = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        headers = {
            "Message-ID": message_id,
            "Date": timestamp,
            "From": sender_info.get("display_name", f"{sender_info.get('name')} <{sender_info.get('email')}>"),
            "Reply-To": sender_info.get("email"),
            "X-Mailer": self._generate_mailer_header(difficulty),
            "X-Originating-IP": self._generate_originating_ip(difficulty),
            "Received": self._generate_received_headers(sender_info, difficulty),
            "MIME-Version": "1.0",
            "Content-Type": "text/html; charset=UTF-8"
        }
        
        return headers
    
    def _apply_spoofing_techniques(self, headers: Dict[str, str], difficulty: DifficultyLevel) -> Dict[str, str]:
        """Apply spoofing techniques based on difficulty level."""
        
        spoofed = headers.copy()
        
        if difficulty == DifficultyLevel.BEGINNER:
            # Obvious spoofing - different display name vs email
            spoofed["From"] = "IT Security Team <suspicious@fake-domain.net>"
            spoofed["Reply-To"] = "noreply@suspicious-site.com"
            
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # Moderate spoofing - subtle domain differences
            original_email = headers["Reply-To"]
            if "@" in original_email:
                local, domain = original_email.split("@", 1)
                # Slight domain modification
                spoofed_domain = domain.replace(".com", ".co").replace("company", "corp")
                spoofed["Reply-To"] = f"{local}@{spoofed_domain}"
                
        elif difficulty >= DifficultyLevel.ADVANCED:
            # Sophisticated spoofing - subdomain spoofing
            original_email = headers["Reply-To"]
            if "@" in original_email:
                local, domain = original_email.split("@", 1)
                # Subdomain spoofing
                spoofed["Reply-To"] = f"{local}@security.{domain}"
                spoofed["X-Original-Sender"] = original_email  # Add confusion header
        
        return spoofed
    
    def _generate_auth_headers(self, headers: Dict[str, str], difficulty: DifficultyLevel) -> Dict[str, str]:
        """Generate authentication headers (SPF, DKIM, DMARC) with appropriate realism."""
        
        auth_headers = {}
        
        if difficulty == DifficultyLevel.BEGINNER:
            # Failed authentication (obvious red flag)
            auth_headers.update({
                "Authentication-Results": "spf=fail (sender IP not authorized)",
                "X-SPF-Result": "fail",
                "X-DKIM-Result": "fail (no valid signature)",
                "X-DMARC-Result": "fail"
            })
            
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # Mixed authentication results (requires closer inspection)
            auth_headers.update({
                "Authentication-Results": "spf=softfail; dkim=pass; dmarc=pass",
                "X-SPF-Result": "softfail", 
                "X-DKIM-Result": "pass (signed by different domain)",
                "X-DMARC-Result": "pass (alignment relaxed)"
            })
            
        else:
            # Sophisticated spoofing (passes most checks)
            auth_headers.update({
                "Authentication-Results": "spf=pass; dkim=pass; dmarc=pass", 
                "X-SPF-Result": "pass",
                "X-DKIM-Result": "pass",
                "X-DMARC-Result": "pass",
                "X-Forged-Headers": "subtle discrepancies present"  # Hint for advanced users
            })
        
        return auth_headers
    
    def _generate_mailer_header(self, difficulty: DifficultyLevel) -> str:
        """Generate X-Mailer header with appropriate realism."""
        
        legitimate_mailers = [
            "Microsoft Outlook 16.0",
            "Apple Mail (16.0)",
            "Mozilla Thunderbird 102.0",
            "Gmail API v1"
        ]
        
        suspicious_mailers = [
            "MailBot v2.1",
            "BulkSender Pro",
            "PhishKit 3.0",
            "Unknown Mailer"
        ]
        
        if difficulty == DifficultyLevel.BEGINNER:
            import random
            return random.choice(suspicious_mailers)
        else:
            import random
            return random.choice(legitimate_mailers)
    
    def _generate_originating_ip(self, difficulty: DifficultyLevel) -> str:
        """Generate X-Originating-IP with appropriate suspicion level."""
        
        if difficulty == DifficultyLevel.BEGINNER:
            # Obviously suspicious IP ranges
            return "192.168.1.100"  # Private IP (red flag)
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # Geographically suspicious
            return "185.220.101.50"  # Known Tor exit node range
        else:
            # Appears legitimate
            return "40.107.103.25"  # Microsoft IP range
    
    def _generate_received_headers(self, sender_info: Dict[str, Any], difficulty: DifficultyLevel) -> str:
        """Generate Received header chain."""
        
        sender_domain = sender_info.get("email", "unknown.com").split("@")[1] if "@" in sender_info.get("email", "") else "unknown.com"
        
        if difficulty == DifficultyLevel.BEGINNER:
            # Simple, obviously spoofed chain
            return f"from suspicious-server.net by mail.{sender_domain} with SMTP"
            
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            # More realistic but with subtle red flags
            return f"from mail.{sender_domain} (mail.{sender_domain} [185.220.101.50]) by mx.recipient.com with ESMTP"
            
        else:
            # Sophisticated, appears legitimate
            return f"from mail.{sender_domain} (mail.{sender_domain} [40.107.103.25]) by mx.recipient.com with ESMTPS (TLS1.2)"
    
    def _identify_header_red_flags(
        self,
        headers: Dict[str, str],
        auth_headers: Dict[str, str],
        difficulty: DifficultyLevel
    ) -> List[Dict[str, Any]]:
        """Identify red flags in email headers for educational purposes."""
        
        red_flags = []
        
        # Check From vs Reply-To mismatch
        from_header = headers.get("From", "")
        reply_to = headers.get("Reply-To", "")
        
        if reply_to and reply_to not in from_header:
            red_flags.append({
                "type": "sender_mismatch",
                "description": "Reply-To address differs from sender address",
                "severity": "medium",
                "location": "From/Reply-To headers",
                "educational_note": "Always check if reply address matches sender"
            })
        
        # Check authentication failures
        auth_results = auth_headers.get("Authentication-Results", "")
        if "fail" in auth_results:
            red_flags.append({
                "type": "auth_failure",
                "description": "Email failed authentication checks (SPF/DKIM/DMARC)",
                "severity": "high",
                "location": "Authentication headers",
                "educational_note": "Failed authentication suggests spoofing"
            })
        
        # Check suspicious mailer
        mailer = headers.get("X-Mailer", "")
        suspicious_terms = ["bot", "bulk", "phish", "unknown"]
        if any(term in mailer.lower() for term in suspicious_terms):
            red_flags.append({
                "type": "suspicious_mailer",
                "description": "Email client appears to be automated or suspicious",
                "severity": "medium",
                "location": "X-Mailer header",
                "educational_note": "Legitimate emails use standard email clients"
            })
        
        # Check originating IP
        orig_ip = headers.get("X-Originating-IP", "")
        if orig_ip.startswith("192.168.") or orig_ip.startswith("10."):
            red_flags.append({
                "type": "private_ip",
                "description": "Email originated from private IP address",
                "severity": "high",
                "location": "X-Originating-IP header",
                "educational_note": "Legitimate emails don't come from private networks"
            })
        
        return red_flags
    
    def _get_applied_techniques(self, headers: Dict[str, str], difficulty: DifficultyLevel) -> List[str]:
        """Get list of spoofing techniques applied."""
        
        techniques = []
        
        from_header = headers.get("From", "")
        reply_to = headers.get("Reply-To", "")
        
        if reply_to and reply_to not in from_header:
            techniques.append("reply_to_spoofing")
        
        if "fake" in from_header.lower() or "suspicious" in from_header.lower():
            techniques.append("obvious_domain_spoofing")
        elif ".co" in reply_to or "corp" in reply_to:
            techniques.append("subtle_domain_spoofing")
        elif "security." in reply_to:
            techniques.append("subdomain_spoofing")
        
        return techniques
    
    def _get_educational_focus(self, red_flags: List[Dict[str, Any]]) -> List[str]:
        """Get educational focus areas based on red flags."""
        
        focus_areas = []
        
        for flag in red_flags:
            if flag["type"] == "sender_mismatch":
                focus_areas.append("verify_sender_consistency")
            elif flag["type"] == "auth_failure":
                focus_areas.append("understand_email_authentication")
            elif flag["type"] == "suspicious_mailer":
                focus_areas.append("recognize_automated_attacks")
            elif flag["type"] == "private_ip":
                focus_areas.append("understand_network_origins")
        
        return list(set(focus_areas))  # Remove duplicates
    
    def _track_header_generation(self, header_data: Dict[str, Any], scenario_context: Dict[str, Any]) -> None:
        """Track header generation for analytics."""
        
        session_id = scenario_context.get("session_id", "unknown") if scenario_context else "unknown"
        
        if session_id not in self.spoofing_history:
            self.spoofing_history[session_id] = []
        
        self.spoofing_history[session_id].append({
            "techniques": header_data["metadata"]["spoofing_techniques"],
            "red_flags_count": len(header_data["red_flags"]),
            "difficulty": header_data["metadata"]["difficulty"]
        })
        
        print(f"[HeaderSpoofing] Applied techniques: {header_data['metadata']['spoofing_techniques']}")
        print(f"[HeaderSpoofing] Generated {len(header_data['red_flags'])} red flags")
