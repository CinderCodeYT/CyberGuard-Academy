# 🚀 CyberGuard Academy - Quick Start Guide

## Prerequisites

- **Python 3.12+**
- **Google AI API Key** (free from https://aistudio.google.com/app/apikey)
- **uv** package manager (recommended) or pip

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/CinderCodeYT/CyberGuard-Academy.git
cd CyberGuard-Academy
```

### 2. Install Dependencies

**Using uv (recommended):**
```bash
uv sync
```

**Using pip:**
```bash
pip install -e .
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google AI API key
vim .env  # or use your preferred editor
```

**Required configuration in `.env`:**
```
GOOGLE_API_KEY=your_api_key_here
```

Get your free API key from: https://aistudio.google.com/app/apikey

## 🎮 Running the Application

### Option 1: Standalone Demo (Command Line)

Run a simple demonstration scenario:
```bash
python main.py
```

This will:
- Initialize all agents
- Run a sample phishing scenario
- Display the conversation and evaluation results
- Show score and learning feedback

### Option 2: Full Web Application (Recommended)

**Step 1: Start the API Server**
```bash
python api.py
```

The API will be available at: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

**Step 2: Start the Streamlit UI** (in a new terminal)
```bash
streamlit run ui.py
```

The UI will open automatically in your browser at: http://localhost:8501

### Option 3: Quick Start Script

For convenience, use the startup script:
```bash
./start.sh
```

This will automatically:
- Check your environment configuration
- Start both API and UI servers
- Open the application in your browser

## 🎯 Using the Training Interface

### In the Streamlit UI:

1. **Configure Your Scenario** (in the sidebar):
   - Select **Threat Type** (phishing, vishing, BEC, etc.)
   - Choose **Difficulty Level** (1-5)
   - Set your **User Role** (for personalized scenarios)

2. **Start Training**:
   - Click **"Start Training"** button
   - Read the opening scenario presented by the Game Master

3. **Interact with the Scenario**:
   - Type responses in the chat interface
   - Use action buttons:
     - 🚨 **Report Phishing** - Report suspicious content
     - 🔗 **Click Link** - Simulate clicking a suspicious link
     - ❓ **Request Hint** - Get guidance if stuck
     - ✅ **Complete Scenario** - End the training

4. **Review Your Results**:
   - View your **Overall Score** (0-100)
   - Check your **Risk Level** (Low, Moderate, High, Critical)
   - Review **Component Scores** (Recognition, Response Time, etc.)
   - Read **Vulnerability Analysis** and **Recommendations**

## 📊 Understanding Your Evaluation

### Score Components

- **Recognition (40%)**: How quickly you identified the threat
- **Response Time (20%)**: Speed of your security response
- **Action Quality (30%)**: Appropriateness of your actions
- **Confidence (10%)**: Your certainty in decisions

### Risk Levels

- 🟢 **Low (80-100)**: Excellent security awareness
- 🟡 **Moderate (60-79)**: Good, with room for improvement
- 🟠 **High (40-59)**: Concerning gaps, needs attention
- 🔴 **Critical (<40)**: Significant vulnerabilities, immediate training needed

## 🔧 Architecture Overview

```
┌─────────────────────────────────────────┐
│         Streamlit UI (ui.py)            │
│    - Chat interface                     │
│    - Configuration panel                │
│    - Results dashboard                  │
└──────────────┬──────────────────────────┘
               │ HTTP Requests
               ▼
┌─────────────────────────────────────────┐
│       FastAPI Backend (api.py)          │
│    - RESTful API endpoints              │
│    - Session management                 │
│    - Request/response handling          │
└──────────────┬──────────────────────────┘
               │ Function Calls
               ▼
┌─────────────────────────────────────────┐
│    Orchestrator (main.py)               │
│    - Agent coordination                 │
│    - Session lifecycle                  │
│    - A2A message passing                │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴─────────────┬───────────┐
    ▼                        ▼           ▼
┌──────────┐        ┌───────────┐   ┌──────────┐
│   Game   │        │  Threat   │   │ Evalua-  │
│  Master  │───────▶│  Actors   │   │  tion    │
│  Agent   │        │  (Phish)  │   │  Agent   │
└──────────┘        └───────────┘   └──────────┘
    │                                     │
    │                                     │
    └──────────────┬──────────────────────┘
                   ▼
            ┌──────────────┐
            │   Memory     │
            │   Manager    │
            └──────────────┘
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific test files:
```bash
pytest tests/test_evaluation_agent.py -v
pytest tests/test_memory_manager.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=cyberguard --cov=agents --cov-report=html
```

## 📝 API Endpoints

### Core Endpoints

- **POST /sessions** - Create a new training session
- **POST /sessions/action** - Process user action
- **POST /sessions/{session_id}/complete** - Complete session and get evaluation
- **GET /sessions/{session_id}** - Get session state
- **GET /user/{user_id}/profile** - Get user profile and progress

### Health & Monitoring

- **GET /health** - Health check
- **GET /** - API information
- **GET /docs** - Interactive API documentation

## 🐛 Troubleshooting

### API Server Not Starting

**Problem:** Port 8000 already in use
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Streamlit Connection Error

**Problem:** Can't connect to API
- Ensure API server is running: `python api.py`
- Check API health: `curl http://localhost:8000/health`
- Verify API_BASE_URL in ui.py matches your API server

### Missing API Key Error

**Problem:** `GOOGLE_API_KEY` not found
- Ensure `.env` file exists in project root
- Verify `GOOGLE_API_KEY=your_key` is set
- Restart the API server after updating `.env`

### Import Errors

**Problem:** Module not found
```bash
# Reinstall dependencies
uv sync --all-packages
# or
pip install -e .
```

## 🎓 Training Best Practices

1. **Start with Lower Difficulty** - Build confidence before advancing
2. **Try Different Roles** - Experience various personalized scenarios
3. **Use Hints Sparingly** - Challenge yourself to recognize threats independently
4. **Review Recommendations** - Focus on specific areas identified in evaluations
5. **Practice Regularly** - Consistent training improves retention

## 📚 Additional Resources

- **Full README**: See [README.md](README.md) for complete project details
- **Copilot Instructions**: See [.github/copilot-instructions.md](.github/copilot-instructions.md) for architecture

## 🤝 Contributing

Contributions are welcome! Please see the main README for contribution guidelines.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

---

**Built with:**
- 🤖 Google Agent Development Kit (ADK)
- 🧠 Gemini 2.5 Pro & Flash
- ⚡ FastAPI & Streamlit
- 🐍 Python 3.12+

**Start training and level up your cybersecurity awareness! 🛡️**
