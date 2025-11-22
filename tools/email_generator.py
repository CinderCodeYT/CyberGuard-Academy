"""
Email Generator Tool - Phishing email content generation for training scenarios.

Generates realistic phishing emails for training purposes:
1. Creates convincing email content based on social engineering patterns
2. Adapts complexity to user role and difficulty level
3. Embeds appropriate red flags for educational value
4. Ensures all content is safe and uses no real credentials
5. Tracks generated content for evaluation analytics

Key principle: Emails should be realistic enough to challenge users
while maintaining clear educational value and safety constraints.
"""

from typing import Dict, Any, List

from cyberguard.models import (
    SocialEngineeringPattern,
    DifficultyLevel,
    UserRole,
    CyberGuardSession,
)

class EmailGenerator:
    """
    Phishing email generation for adaptive training scenarios.
    
    Generates realistic but safe phishing emails that challenge users
    while providing clear learning opportunities through embedded red flags.
    """

    def __init__(self):
        self.email_templates = {}
        self.email_history = {}
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize email templates and generation tracking"""
        print("[EmailGenerator] Email generator initialized")
        pass

    async def shutdown(self) -> None:
        """Clean up resources"""
        print("[EmailGenerator] Email generator shutting down")
        self.email_templates.clear()
        self.email_history.clear()

    async def generate_phishing_email(
        self,
        threat_pattern: SocialEngineeringPattern,
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        session_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate phishing email content for training.
        
        Args:
            threat_pattern: Social engineering pattern to use
            user_role: Target user's job function
            difficulty_level: Complexity level for the email
            session_context: Additional context for personalization
            
        Returns:
            Generated email with metadata for evaluation
        """
        # Select base template based on pattern and role
        template = self._select_email_template(threat_pattern, user_role, difficulty_level)
        
        # Generate email components
        sender = self._generate_sender(template, user_role)
        subject = self._generate_subject(template, threat_pattern, difficulty_level)
        body = self._generate_body(template, threat_pattern, user_role, difficulty_level)
        attachments = self._generate_attachments(template, difficulty_level)
        
        # Embed red flags for educational value
        red_flags = self._embed_red_flags(sender, subject, body, difficulty_level)
        
        email_content = {
            "sender": sender,
            "subject": subject, 
            "body": body,
            "attachments": attachments,
            "red_flags": red_flags,
            "metadata": {
                "pattern": threat_pattern.value,
                "difficulty": difficulty_level.value,
                "target_role": user_role.value,
                "educational_focus": template.get("learning_objectives", [])
            }
        }
        
        return email_content
    
    def _select_email_template(
        self, 
        pattern: SocialEngineeringPattern, 
        role: UserRole, 
        difficulty: DifficultyLevel
    ) -> Dict[str, Any]:
        """Select appropriate email template based on context."""
        
        # Template database (in production, this would be from a database)
        templates = {
            SocialEngineeringPattern.URGENCY: {
                UserRole.GENERAL: {
                    "scenario": "account_suspension",
                    "sender_type": "security_team", 
                    "urgency_level": "high",
                    "learning_objectives": ["verify_sender", "check_urgency_claims"]
                },
                UserRole.FINANCE: {
                    "scenario": "payment_verification",
                    "sender_type": "bank_security",
                    "urgency_level": "high",
                    "learning_objectives": ["verify_financial_requests", "check_domain"]
                }
            },
            SocialEngineeringPattern.AUTHORITY: {
                UserRole.GENERAL: {
                    "scenario": "it_policy_update",
                    "sender_type": "it_admin",
                    "authority_level": "high",
                    "learning_objectives": ["verify_authority", "check_internal_processes"]
                }
            },
            SocialEngineeringPattern.CURIOSITY: {
                UserRole.GENERAL: {
                    "scenario": "bonus_announcement",
                    "sender_type": "hr_team",
                    "curiosity_hook": "confidential_info",
                    "learning_objectives": ["verify_hr_communications", "be_suspicious_of_unexpected_news"]
                }
            }
        }
        
        # Get template or fallback to general pattern
        return templates.get(pattern, {}).get(role, templates[pattern].get(UserRole.GENERAL, {}))
    
    def _generate_sender(self, template: Dict[str, Any], user_role: UserRole) -> Dict[str, Any]:
        """Generate sender information with appropriate spoofing level."""
        
        sender_templates = {
            "security_team": {
                "name": "IT Security Team",
                "email": "security@company-alerts.net",  # Slight domain variation 
                "display_name": "Corporate Security <security@company-alerts.net>",
                "red_flags": ["domain_variation"]
            },
            "it_admin": {
                "name": "System Administrator", 
                "email": "admin@company-it.org",
                "display_name": "IT Admin <admin@company-it.org>",
                "red_flags": ["generic_title", "domain_variation"]
            },
            "bank_security": {
                "name": "Bank Security Alert",
                "email": "alerts@bank-security.net",
                "display_name": "Bank Security <alerts@bank-security.net>", 
                "red_flags": ["external_domain"]
            },
            "hr_team": {
                "name": "Human Resources",
                "email": "hr@company-updates.com",
                "display_name": "HR Team <hr@company-updates.com>",
                "red_flags": ["domain_variation"]
            }
        }
        
        sender_type = template.get("sender_type", "security_team")
        return sender_templates.get(sender_type, sender_templates["security_team"])
    
    def _generate_subject(
        self, 
        template: Dict[str, Any], 
        pattern: SocialEngineeringPattern, 
        difficulty: DifficultyLevel
    ) -> str:
        """Generate subject line based on social engineering pattern."""
        
        subjects = {
            SocialEngineeringPattern.URGENCY: [
                "URGENT: Account Suspension Notice",
                "IMMEDIATE ACTION REQUIRED - Security Alert", 
                "Your account will be closed in 24 hours",
                "FINAL NOTICE: Verify your account immediately"
            ],
            SocialEngineeringPattern.AUTHORITY: [
                "New IT Policy - Immediate Compliance Required",
                "CEO Directive: Update Your Credentials",
                "System Administrator: Mandatory Password Reset",
                "IT Security: Policy Violation Detected"
            ],
            SocialEngineeringPattern.CURIOSITY: [
                "Confidential: Your 2024 Bonus Information",
                "You've received a confidential message",
                "Private: Important update about your role",
                "Exclusive: Company announcement inside"
            ]
        }
        
        # Select random subject from appropriate pattern
        import random
        pattern_subjects = subjects.get(pattern, subjects[SocialEngineeringPattern.URGENCY])
        
        # Add complexity based on difficulty (lower difficulty = more obvious red flags)
        if difficulty == DifficultyLevel.BEGINNER:
            # Add obvious red flags like ALL CAPS or excessive punctuation
            subject = random.choice(pattern_subjects)
            if "URGENT" not in subject:
                subject = f"URGENT!!! {subject}"
            return subject
        
        return random.choice(pattern_subjects)
    
    def _generate_body(
        self, 
        template: Dict[str, Any], 
        pattern: SocialEngineeringPattern, 
        role: UserRole,
        difficulty: DifficultyLevel
    ) -> str:
        """Generate email body content with appropriate sophistication level."""
        
        # Body templates by scenario
        body_templates = {
            "account_suspension": f"""
Dear User,

We have detected suspicious activity on your account that requires immediate verification.

Your account will be suspended within 24 hours unless you verify your identity by clicking the link below:

[VERIFY ACCOUNT NOW]

If you do not complete verification, you will lose access to all company systems.

Best regards,
IT Security Team
            """,
            "payment_verification": f"""
Dear {role.value.replace('_', ' ').title()} Team Member,

We have flagged a payment transaction that requires your immediate attention.

Transaction: $2,847.99 - Requires Authorization
Status: PENDING VERIFICATION

Please verify this transaction immediately: [AUTHORIZE PAYMENT]

Failure to respond within 2 hours will result in account restrictions.

Security Team
First National Bank
            """,
            "it_policy_update": f"""
Dear Employee,

As part of our new cybersecurity policy, all employees must update their login credentials.

This is a mandatory update required by our security compliance team.

Update your credentials here: [UPDATE PASSWORD]

Employees who do not complete this update by end of day will be locked out of systems.

IT Administrator
Corporate IT Department
            """,
            "bonus_announcement": f"""
Dear Team Member,

Congratulations! You have been selected for a special bonus program.

Your bonus amount: $1,250.00
Eligibility expires: Today

View your bonus details: [CLAIM BONUS]

This information is confidential - please do not share with other employees.

Human Resources Department
            """
        }
        
        scenario = template.get("scenario", "account_suspension")
        body = body_templates.get(scenario, body_templates["account_suspension"])
        
        # Add difficulty-appropriate red flags
        if difficulty == DifficultyLevel.BEGINNER:
            # Add obvious spelling/grammar errors
            body = body.replace("suspicious", "suspicous")
            body = body.replace("immediately", "immediatley") 
            body += "\n\nSend us your password to: security@temp-mail.com"
        
        return body.strip()
    
    def _generate_attachments(self, template: Dict[str, Any], difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Generate safe attachment metadata (no actual files)."""
        
        if difficulty <= DifficultyLevel.INTERMEDIATE:
            return []  # No attachments for easier scenarios
        
        # Advanced scenarios might include suspicious attachments
        return [
            {
                "filename": "SecurityUpdate.pdf.exe",  # Double extension red flag
                "type": "executable", 
                "description": "Suspicious double extension",
                "red_flags": ["double_extension", "executable_disguised_as_pdf"]
            }
        ]
    
    def _embed_red_flags(
        self, 
        sender: Dict[str, Any], 
        subject: str, 
        body: str, 
        difficulty: DifficultyLevel
    ) -> List[Dict[str, Any]]:
        """Catalog red flags for educational debrief."""
        
        red_flags = []
        
        # Sender red flags
        if "domain_variation" in sender.get("red_flags", []):
            red_flags.append({
                "type": "sender_domain",
                "description": "Sender domain doesn't match claimed organization",
                "severity": "high",
                "location": "sender_email"
            })
        
        # Subject red flags  
        if "URGENT" in subject or "!!!" in subject:
            red_flags.append({
                "type": "artificial_urgency", 
                "description": "Excessive urgency language designed to pressure quick action",
                "severity": "medium",
                "location": "subject_line"
            })
        
        # Body red flags
        if "click" in body.lower() and ("immediately" in body.lower() or "now" in body.lower()):
            red_flags.append({
                "type": "urgent_action_request",
                "description": "Combines urgency with immediate action request", 
                "severity": "high",
                "location": "email_body"
            })
        
        if any(word in body.lower() for word in ["password", "credentials", "login"]):
            red_flags.append({
                "type": "credential_request",
                "description": "Requests sensitive authentication information",
                "severity": "high", 
                "location": "email_body"
            })
        
        return red_flags
    
    def _track_email_generation(self, email_content: Dict[str, Any], session_context: Dict[str, Any]) -> None:
        """Track generated emails for analytics and avoiding repetition."""
        
        session_id = session_context.get("session_id", "unknown") if session_context else "unknown"
        
        if session_id not in self.email_history:
            self.email_history[session_id] = []
        
        self.email_history[session_id].append({
            "pattern": email_content["metadata"]["pattern"],
            "difficulty": email_content["metadata"]["difficulty"],
            "subject": email_content["subject"],
            "red_flags_count": len(email_content["red_flags"])
        })