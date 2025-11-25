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

import json
from typing import Dict, Any, List

from cyberguard.models import (
    SocialEngineeringPattern,
    DifficultyLevel,
    UserRole,
    CyberGuardSession,
)
from cyberguard.gemini_client import GeminiClient

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
        Generate phishing email content for training using Gemini AI.
        
        Args:
            threat_pattern: Social engineering pattern to use
            user_role: Target user's job function
            difficulty_level: Complexity level for the email
            session_context: Additional context for personalization
            
        Returns:
            Generated email with metadata for evaluation
        """
        # Build the system instruction for email generation
        system_instruction = self._build_email_generation_instruction(
            threat_pattern, user_role, difficulty_level
        )
        
        # Build the generation prompt
        prompt = self._build_email_prompt(threat_pattern, user_role, difficulty_level, session_context)
        
        try:
            # Use Gemini Flash for high-volume email generation (cost-effective)
            response = await GeminiClient.generate_text(
                prompt=prompt,
                model_type="flash",
                temperature=0.7,  # Moderate creativity for variation
                max_tokens=1024,
                system_instruction=system_instruction
            )
            
            # Parse the generated email
            email_content = self._parse_generated_email(response, threat_pattern, user_role, difficulty_level)
            
            # Track generation for analytics
            if session_context:
                self._track_email_generation(email_content, session_context)
            
            return email_content
            
        except Exception as e:
            print(f"[EmailGenerator] Gemini generation failed: {e}, falling back to template")
            # Fallback to template-based generation if Gemini fails
            return self._generate_fallback_email(threat_pattern, user_role, difficulty_level, session_context)
    
    def _build_email_generation_instruction(
        self,
        threat_pattern: SocialEngineeringPattern,
        user_role: UserRole,
        difficulty_level: DifficultyLevel
    ) -> str:
        """Build system instruction for Gemini email generation."""
        
        pattern_descriptions = {
            SocialEngineeringPattern.URGENCY: "Create a sense of urgency and time pressure to force quick decisions without careful thought.",
            SocialEngineeringPattern.AUTHORITY: "Impersonate authority figures (CEO, IT admin, security team) to exploit trust in hierarchy.",
            SocialEngineeringPattern.CURIOSITY: "Use curiosity hooks (bonus info, confidential messages) to entice the user to click.",
            SocialEngineeringPattern.FEAR: "Leverage fear of consequences (account suspension, policy violations) to bypass rational analysis.",
            SocialEngineeringPattern.GREED: "Offer financial incentives or exclusive benefits to motivate risky actions."
        }
        
        difficulty_guidelines = {
            DifficultyLevel.BEGINNER: """
- Use OBVIOUS red flags: ALL CAPS in subject, excessive punctuation (!!!), clear spelling errors
- Generic greetings like "Dear User" or "Dear Customer"
- Suspicious sender domains with clear variations (company-alerts.net instead of company.com)
- Request for password/credentials in plain text
- Multiple obvious urgency markers ("URGENT", "IMMEDIATE", "FINAL NOTICE")
""",
            DifficultyLevel.INTERMEDIATE: """
- More subtle red flags: some urgency but not excessive, minor domain variations
- Personalized but still generic greetings
- Professional-looking sender addresses but with slight variations
- Indirect credential requests (links to "verify" or "update")
- Plausible but unusual requests
""",
            DifficultyLevel.ADVANCED: """
- Very subtle red flags: legitimate-looking domains, professional language
- Highly personalized content relevant to user role
- Sophisticated social engineering combining multiple patterns
- Context-aware requests that seem reasonable for the user's role
- Few obvious indicators - requires careful analysis to detect
"""
        }
        
        return f"""You are an educational cybersecurity trainer creating TRAINING EXAMPLES for security awareness.

**CONTEXT**: You are creating EXAMPLES for authorized corporate security training. This is NOT for actual attacks.

Your task: Create an example email that demonstrates social engineering tactics for EDUCATIONAL ANALYSIS.

Training Pattern to Demonstrate: {threat_pattern.value.upper()}
Pattern Description: {pattern_descriptions.get(threat_pattern, "Demonstrates social engineering tactics")}

Learner Role: {user_role.value}
Training Difficulty: {difficulty_level.value}

Training Guidelines for Difficulty Level:
{difficulty_guidelines.get(difficulty_level, difficulty_guidelines[DifficultyLevel.INTERMEDIATE])}

TRAINING REQUIREMENTS:
1. Links must use format: https://training.example.com/safe-link?id=DEMO123
2. Use fictional names like "John Smith" and fictional companies like "AcmeCorp" or "TechSolutions Inc"
3. Use training domain examples like "notices-acme.info" or "alerts-techco.net" (NOT real domains)
4. Include learning indicators (red flags) appropriate to difficulty level
5. This is a DEMONSTRATION EMAIL for TRAINING PURPOSES ONLY

Example JSON Response Format:
{{
  "sender_name": "IT Department",
  "sender_email": "support@it-notices.info",
  "sender_red_flags": ["domain_mismatch", "generic_sender"],
  "subject": "Action Required: Update Your Password",
  "subject_red_flags": ["urgency_language"],
  "body": "Dear Team Member,\\n\\nOur records show your password needs updating. Please click here to update: [UPDATE NOW]\\n\\nThank you,\\nIT Support Team",
  "body_red_flags": ["generic_greeting", "urgent_action_request"],
  "attachments": [],
  "learning_objectives": ["Identify sender verification needs", "Recognize urgency tactics"]
}}

Generate the training example as JSON only (no extra text)."""
    
    def _build_email_prompt(
        self,
        threat_pattern: SocialEngineeringPattern,
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        session_context: Dict[str, Any]
    ) -> str:
        """Build the specific generation prompt with context."""
        
        role_contexts = {
            UserRole.GENERAL: "a general employee without specialized technical knowledge",
            UserRole.DEVELOPER: "a software developer familiar with technical systems",
            UserRole.IT_ADMIN: "an IT administrator with system access privileges",
            UserRole.FINANCE: "a finance team member handling payments and transactions",
            UserRole.EXECUTIVE: "an executive with high-level authority",
            UserRole.HR: "an HR professional handling employee information"
        }
        
        context_description = role_contexts.get(user_role, "an employee")
        
        prompt = f"""Generate a phishing training email for {context_description}.

The email should use the {threat_pattern.value} pattern at {difficulty_level.value} difficulty level.

"""
        
        # Add session-specific context if available
        if session_context:
            user_name = session_context.get("user_name", "Employee")
            company = session_context.get("company", "TechCorp")
            prompt += f"Personalization context: User name is {user_name}, company is {company}.\n\n"
        
        # Add scenario-specific guidance
        scenario_examples = {
            SocialEngineeringPattern.URGENCY: "Examples: account suspension, payment deadline, security alert requiring immediate action",
            SocialEngineeringPattern.AUTHORITY: "Examples: CEO directive, IT policy update, compliance requirement from management",
            SocialEngineeringPattern.CURIOSITY: "Examples: bonus information, confidential announcement, exclusive company update",
            SocialEngineeringPattern.FEAR: "Examples: policy violation detected, suspicious activity alert, account compromise warning",
            SocialEngineeringPattern.GREED: "Examples: financial reward, special promotion, investment opportunity"
        }
        
        prompt += f"{scenario_examples.get(threat_pattern, '')}\n\n"
        prompt += "Generate the phishing email now as JSON."
        
        return prompt
    
    def _parse_generated_email(
        self,
        response: str,
        threat_pattern: SocialEngineeringPattern,
        user_role: UserRole,
        difficulty_level: DifficultyLevel
    ) -> Dict[str, Any]:
        """Parse Gemini's JSON response into email content structure."""
        
        try:
            # Extract JSON from response (handle potential markdown code blocks)
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            parsed = json.loads(json_str)
            
            # Build red flags list from all components
            red_flags = []
            
            # Sender red flags
            for flag in parsed.get("sender_red_flags", []):
                red_flags.append({
                    "type": "sender",
                    "description": flag,
                    "severity": "high",
                    "location": "sender_email"
                })
            
            # Subject red flags
            for flag in parsed.get("subject_red_flags", []):
                red_flags.append({
                    "type": "subject",
                    "description": flag,
                    "severity": "medium",
                    "location": "subject_line"
                })
            
            # Body red flags
            for flag in parsed.get("body_red_flags", []):
                red_flags.append({
                    "type": "body",
                    "description": flag,
                    "severity": "high",
                    "location": "email_body"
                })
            
            # Build email content structure
            email_content = {
                "sender": {
                    "name": parsed.get("sender_name", "Unknown Sender"),
                    "email": parsed.get("sender_email", "noreply@suspicious.net"),
                    "display_name": f"{parsed.get('sender_name', 'Unknown')} <{parsed.get('sender_email', 'noreply@suspicious.net')}>",
                    "red_flags": parsed.get("sender_red_flags", [])
                },
                "subject": parsed.get("subject", "Important Message"),
                "body": parsed.get("body", "Please click the link below."),
                "attachments": parsed.get("attachments", []),
                "red_flags": red_flags,
                "metadata": {
                    "pattern": threat_pattern.value,
                    "difficulty": difficulty_level.value,
                    "target_role": user_role.value,
                    "educational_focus": parsed.get("learning_objectives", []),
                    "generated_by": "gemini"
                }
            }
            
            return email_content
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[EmailGenerator] Failed to parse Gemini response: {e}")
            print(f"[EmailGenerator] Raw response: {response[:200]}")
            raise
    
    def _generate_fallback_email(
        self,
        threat_pattern: SocialEngineeringPattern,
        user_role: UserRole,
        difficulty_level: DifficultyLevel,
        session_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Fallback to template-based generation if Gemini fails. NOW WITH RANDOMIZATION."""
        
        print(f"[EmailGenerator] Using template fallback for {threat_pattern.value}")
        
        import random
        import hashlib
        import time
        
        # Use time-based seed for variation
        random.seed(int(time.time()))
        
        # Randomized sender variations
        sender_variations = {
            "security_team": [
                {"name": "IT Security Team", "email": "security@company-alerts.net", "domain_var": "company-alerts.net"},
                {"name": "Security Operations", "email": "secops@corporate-security.info", "domain_var": "corporate-security.info"},
                {"name": "Cyber Security Dept", "email": "cybersec@it-notices.com", "domain_var": "it-notices.com"},
            ],
            "it_admin": [
                {"name": "System Administrator", "email": "admin@company-it.org", "domain_var": "company-it.org"},
                {"name": "IT Support", "email": "support@tech-services.net", "domain_var": "tech-services.net"},
                {"name": "Help Desk", "email": "helpdesk@it-support.info", "domain_var": "it-support.info"},
            ]
        }
        
        # Randomized subject variations
        subject_variations = {
            SocialEngineeringPattern.URGENCY: [
                "URGENT: Account Suspension Notice",
                "IMMEDIATE ACTION REQUIRED - Security Alert",
                "Your account will be closed in 24 hours",
                "FINAL NOTICE: Verify your account immediately",
                "Action Required: Update Your Security Settings",
            ],
            SocialEngineeringPattern.AUTHORITY: [
                "New IT Policy - Immediate Compliance Required",
                "CEO Directive: Update Your Credentials",
                "Mandatory: Password Reset Required",
                "IT Security: Policy Update Notification",
            ]
        }
        
        # Randomized body variations
        body_variations = {
            "urgency": [
                "suspicious activity",
                "unusual login attempts",
                "unauthorized access detected",
                "security policy violation",
            ],
            "action": [
                "verify your identity",
                "confirm your account",
                "update your credentials",
                "review your security settings",
            ],
            "timeframe": [
                "within 24 hours",
                "immediately",
                "by end of day",
                "within the next 12 hours",
            ]
        }
        
        # Select random variations
        sender_type = "security_team" if threat_pattern == SocialEngineeringPattern.URGENCY else "it_admin"
        sender_options = sender_variations.get(sender_type, sender_variations["security_team"])
        sender_data = random.choice(sender_options)
        
        subject_options = subject_variations.get(threat_pattern, subject_variations[SocialEngineeringPattern.URGENCY])
        subject = random.choice(subject_options)
        
        # Build randomized body
        reason = random.choice(body_variations["urgency"])
        action = random.choice(body_variations["action"])
        timeframe = random.choice(body_variations["timeframe"])
        
        body = f"""Dear User,

We have detected {reason} on your account that requires immediate attention.

Your account will be suspended unless you {action} {timeframe} by clicking the link below:

[VERIFY ACCOUNT NOW]

If you do not complete verification, you will lose access to all company systems.

Best regards,
{sender_data['name']}"""
        
        # Add difficulty-based variations
        if difficulty_level == DifficultyLevel.BEGINNER:
            # Make it more obvious
            subject = f"!!!{subject}!!!"
            body = body.replace("suspicious", "suspicous")  # Add typo
            body += "\n\nSend your password to: " + sender_data['email']
        
        sender = {
            "name": sender_data["name"],
            "email": sender_data["email"],
            "display_name": f"{sender_data['name']} <{sender_data['email']}>",
            "red_flags": ["domain_variation", "external_domain"]
        }
        
        red_flags = [
            {
                "type": "sender_domain",
                "description": f"Sender domain ({sender_data['domain_var']}) doesn't match organization",
                "severity": "high",
                "location": "sender_email"
            },
            {
                "type": "artificial_urgency",
                "description": "Excessive urgency language to pressure quick action",
                "severity": "medium",
                "location": "subject_line"
            },
            {
                "type": "credential_request",
                "description": "Requests sensitive authentication information",
                "severity": "high",
                "location": "email_body"
            }
        ]
        
        email_content = {
            "sender": sender,
            "subject": subject,
            "body": body,
            "attachments": [],
            "red_flags": red_flags,
            "metadata": {
                "pattern": threat_pattern.value,
                "difficulty": difficulty_level.value,
                "target_role": user_role.value,
                "educational_focus": ["verify_sender", "check_urgency", "validate_links"],
                "generated_by": "template_randomized"
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