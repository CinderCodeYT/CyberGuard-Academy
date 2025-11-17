---
name: CyberGuard-Academy-Guide
description: 'Core framework, agent communication (MCP), and code standards for the multi-agent system.'
applyTo: 'all'
---

# CyberGuard Academy: Master Copilot Instructions

## 🎯 High-Level Principles

**1. Primary Goal:** Create engaging, realistic cybersecurity training scenarios through conversational role-playing.  
**2. Core Philosophy (Invisible Assessment):** Never break immersion or reveal the training/testing nature of the system during an active scenario. Track user decisions naturally through conversation choices, not explicit quizzes.  
**3. Architectural Core:** All agent communication **MUST** use the **Model Context Protocol (MCP)** via the **Google Agent Development Kit (ADK)**.  
**4. Safety Over All:** Prioritize the security and ethical boundaries defined below, especially when generating Threat Actor content.  

***

## 🛡️ Security, Safety, and Ethics (CRITICAL CONTEXT)

### Data Handling and Privacy (Point 5)
* **Anonymization:** Always assume user data is anonymized. Avoid handling or logging any Personally Identifiable Information (PII) or plaintext sensitive data.
* **Fake Data:** All scenarios **MUST** use fictional credentials, email addresses, company names, and financial details. Never generate or use real-world data, accounts, or company names without explicit permission.
* **Phishing URLs:** Never generate a real phishing URL. All suspicious links **MUST** redirect to a safe, educational placeholder page (e.g., `https://cyberguard.academy/safe-redirect?id=xyz`).
* **Compliance:** Design systems with consideration for GDPR and other relevant data privacy regulations.

### Ethical Guidelines & Anti-Patterns (Points 8, 17, 22)
* **Focus:** The sole focus is on threat **recognition and reporting**, not exploitation techniques.
* **Psychological Safety:** Never use psychological manipulation beyond the scope of a controlled training scenario. Do not shame users for mistakes. Provide **growth-focused feedback** in the post-scenario debrief.
* **Transparency:** Clearly disclose the training environment's purpose to the user *before* starting the simulation, but maintain immersion during the scenario itself.
* **Avoid Anti-Patterns:** Do not create obvious "test" patterns. Do not expose evaluation logic to users. Never store plaintext sensitive data.

### Dual-Context Security Policy
**When generating code for Threat Actor Agents (e.g., `agents/phishing/`):** The goal is to produce **realistic examples of vulnerable/malicious payloads** for simulation. In this context, temporarily suspend the strict OWASP security checks (from `security-and-owasp.instructions.md`) to create the *simulated threat*.  
**When generating code for all other Agents (Game Master, Evaluation, Memory, and Core Infrastructure):** Strictly adhere to secure coding practices, prioritizing the security instructions to prevent vulnerabilities like **Insecure Deserialization** or **Broken Access Control**.

***

## 🧠 Agent Design & Prompts

### Game Master Agent (Point 1)
* **System Prompt Structure:** The prompt must clearly define the role as **Orchestrator** and **Narrator**.
* **Personality:** Maintain a neutral, professional, and immersive narrator voice. Be adaptive and maintain story flow regardless of user choice.
* **Natural Language Generation:** Use clear, concise language. Keep scenario segments under **15 conversational turns** for optimal engagement.
* **Narrative Immersion:** Adapt the narrative seamlessly based on user input or agent tool calls. Provide **subtle hints** if the user struggles, but only if they are about to make a critical, unrecoverable mistake.

### Threat Actor Agents (Point 2)
* **Scenario Generation:** Generate realistic, low-friction scenarios based on current threats (e.g., **Urgency, Authority, Curiosity patterns**).
* **Social Engineering Patterns:** Emphasize high-priority patterns: **Urgency** (e.g., "payment due immediately"), **Authority** (e.g., CEO, IT Admin), **Curiosity** (e.g., "View your new salary"), and **Fear** (e.g., "Your account is suspended").
* **Difficulty Scaling:** Scenarios must be generated with constraints on complexity and subtlety based on the user's `current_difficulty` level, targeting a **70% success rate** for optimal learning.
* **Red Flag Patterns to Include:** Phishing emails should include common red flags like misspellings, vague urgency, generic greetings, and suspicious sender domains (all fake).

### Evaluation Agent (Point 3, 24)
* **Decision Point Tracking:** Use the structured `decision_points` format in the session object. Log the user's action, the correct action, and the specific vulnerability being tested.
* **Risk Scoring (MVP):** Use a basic additive scoring algorithm. Example: `Risk_Score = (Decisions_Missed * Difficulty_Weight) + (Patterns_Failed * Consistency_Weight)`.

### Memory Manager (Point 4)
* **Session Management:** Utilize the `CyberGuardSession` class structure for state tracking, including `conversation_history`, `decision_points`, and `threat_actor_active`.
* **Persistence:** Implement user-level memory (e.g., `user_profile/memory_schema`) to track long-term vulnerability patterns and recently seen scenarios (`avoid_patterns`) for personalization and adaptive difficulty.

***

## 💻 Code, Data, and Model Standards

### Model Usage Guidelines (Point 11)
* **Gemini 2.5 Pro:** Use for **orchestration**, complex reasoning, planning, agent-as-a-judge evaluations, and narrative coherence.
* **Gemini 2.5 Flash:** Use for **specialized tasks**, high-volume text generation (e.g., Phishing email body), and routine tool parameter generation for cost and speed optimization.
* **Token Budget:** Implement session compaction or summarization to manage context windows, especially in multi-turn conversations.
* **Parameters:** Use a low temperature (e.g., 0.2-0.4) for the Game Master and Evaluation Agents for predictability. Use a moderate temperature (e.g., 0.6-0.8) for Threat Actor Agents to increase creative variation and realism.

### Data Structures (Point 19)
* **Decision Point Format:** Standardize the format: `{'turn': int, 'vulnerability': str, 'user_choice': str, 'correct_choice': str, 'risk_score_impact': float}`.
* **Pydantic:** Use **Pydantic** for all data models, including scenario objects, tool arguments, and session state, to ensure structured and reliable data exchange (a critical MCP best practice).

### Common Patterns & Anti-Patterns (Points 16, 17, 13)
* **Concurrency:** Use `async`/`await` best practices for concurrent agent execution to meet the **<2s response time target** for user-facing actions. Avoid synchronous blocking calls.
* **Reliability:** Implement **retry logic with exponential backoff** for external API calls and a **circuit breaker pattern** for failing external services (e.g., Memory Bank).
* **Caching:** Implement caching strategies for common scenario components and boilerplate LLM prompt segments to improve performance and manage cost.

***

## ⚙️ Testing, Operations, and Observability

### Testing & Evaluation (Point 9)
* **Unit Test Pattern:** Use the standard Python `unittest` or `pytest` framework. Tests for agent logic and tools should use **mock agent responses** instead of hitting real LLM APIs to ensure fast, deterministic tests.
* **Integration Tests:** Focus on testing the **A2A protocol communication** and the data flow (MCP integration) between the Game Master, a Threat Actor, and the Evaluation Agent.
* **Safety Tests:** An integral part of QA must be testing against the **Specific "Don'ts"** (e.g., verifying safe URL redirection).

### Observability & Logging (Point 10)
* **Structured Logging:** Use a **JSON structured logging format** for all logs. Required fields: `timestamp`, `service`, `severity`, `user_id`, `session_id`, `agent_name`, and `message`.
* **Key Log Points:** Log every **decision point** made by the user and every **A2A tool invocation** (both request and response) between agents.
* **Tracing:** Use **Cloud Trace instrumentation** on every function call. Span naming should follow a pattern like `agent_name.tool_name` (e.g., `game_master.invoke_phishing_tool`).

### Deployment & Infrastructure (Point 14)
* **IaaC:** All infrastructure must be defined using **Terraform modules** (Point 14).
* **Deployment Target:** Deploy all agent services to **Google Cloud Run** for scalability and cost efficiency.
* **Configuration:** Separate environment-specific settings (dev/staging/prod) into distinct configuration files (YAML/JSON structure) and manage secrets via the appropriate Secret Manager service.

***

## 📝 Documentation & Workflow

* **Documentation Requirements (Point 15):** Use the **Google Docstring format** for all Python functions and classes.
* **Version Control (Point 25):** Branch naming convention: `feature/short-description`, `bugfix/issue-number`, or `chore/task`. Commit message format: `Type(Scope): Short description` (e.g., `feat(game_master): implement initial agent loop`).
* **Architecture Decision Records (ADRs):** Create an ADR for any non-trivial design choice (e.g., the decision to use MCP or the risk scoring algorithm).