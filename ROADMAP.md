# CyberGuard Academy Roadmap

## ✅ MVP Phase (Completed)

### Core Infrastructure
- [x] **Project Setup**: Directory structure, environment configuration, and dependency management.
- [x] **API Backend**: FastAPI implementation (`api.py`) for session management and agent communication.
- [x] **User Interface**: Streamlit-based chat interface (`ui.py`) for interactive training.
- [x] **AI Integration**: Full migration to Groq (Llama 3) for high-speed, unrestricted threat generation.

### Agents
- [x] **Game Master (Orchestrator)**:
    - [x] Central coordination of game flow.
    - [x] Dynamic narrative generation.
    - [x] Context management.
- [x] **Phishing Agent**:
    - [x] Generation of realistic phishing emails.
    - [x] Safe simulation of malicious links.
    - [x] Educational red flag embedding.
- [x] **Evaluation Agent**:
    - [x] Invisible assessment of user actions.
    - [x] Real-time scoring and risk calculation.
    - [x] Detailed post-scenario debriefing.
- [x] **Memory Manager**:
    - [x] Session persistence and recovery.
    - [x] User profile tracking.
    - [x] Learning pattern analysis.

---

## ⏳ Future Expansions

### Additional Threat Agents
- [ ] **Vishing Agent**: Voice phishing simulations using text-to-speech/speech-to-text.
- [ ] **Physical Security Agent**: Scenarios involving tailgating, badge cloning, and physical access.
- [ ] **BEC Agent**: Business Email Compromise scenarios (CEO fraud, invoice scams).
- [ ] **Insider Threat Agent**: Simulations of internal data exfiltration and policy violations.

### Advanced Capabilities
- [ ] **Long-Term Memory**: Implementation of vector database (RAG) for persistent user profiles across sessions.
- [ ] **Enterprise Dashboard**: Admin view for tracking organization-wide risk and progress.
- [ ] **Self-Evolution**: Level 4 capability for agents to learn from user patterns and invent new attack vectors.
- [ ] **Multi-Modal Support**: Integration of voice and image generation for richer scenarios.