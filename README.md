# 🧠 AI Brain

An intelligent, hybrid personal AI assistant featuring **Cloud Gemini with Local Gemma Fallback**, **Persistent Multi-Session SQLite Memory**, **ChatGPT-Style Voice Interaction**, and a **Real-Time Performance Dashboard** built with Streamlit.

---

## 🌟 Highlights

- **Hybrid AI Routing:** Fast, high-reasoning cloud responses via **Google Gemini** with automatic, seamless fallback to **Local Gemma (via Ollama)** whenever offline or rate-limited.
- **Persistent Memory:** Complete multi-session conversation history stored in SQLite (`ai_brain.db`). Create new sessions, switch conversations, and resume chats anytime.
- **Hands-Free Voice Pipeline:** Custom ChatGPT-style browser voice composer with offline speech transcription (`faster-whisper` / `SpeechRecognition`) and local speech playback (`pyttsx3`).
- **Observability Dashboard:** Real-time health monitoring, latency comparison charts, RAM usage tracking, token estimation, and cloud cost accounting.
- **Clean Architecture:** Modular design separating presentation, orchestration, model providers, evaluation, and memory.

---

## 📂 Project Structure

```
AI-Brain/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Configuration secrets & model names
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
│
├── assistant/                  # Core AI Brain orchestration
│   ├── config.py               # Central environment configuration
│   ├── router.py               # AI routing logic (Gemini → Gemma)
│   ├── health_check.py         # System health diagnostic checks
│   │
│   ├── evaluation/             # Metrics & tracking
│   │   ├── cost_tracker.py     # Token & USD cost calculator
│   │   └── performance.py      # Latency & RAM profiler
│   │
│   ├── memory/                 # Persistence & context windowing
│   │   ├── context_manager.py  # Window-based history manager
│   │   └── conversation.py     # SQLite persistence engine
│   │
│   ├── providers/              # Model backends
│   │   ├── base.py             # BaseProvider abstract class
│   │   ├── cloud_gemini.py     # Google Gemini REST provider
│   │   └── local_gemma.py      # Ollama local provider
│   │
│   └── voice/                  # Audio I/O pipeline
│       ├── audio_manager.py    # Desktop mic recording & processing
│       ├── speech_to_text.py   # Speech recognition (faster-whisper / SR)
│       └── text_to_speech.py   # Voice synthesizer (pyttsx3)
│
├── interface/                  # Streamlit UI modules
│   ├── chat.py                 # Conversational chat view & message loop
│   ├── dashboard.py            # Performance & observability dashboard
│   ├── voice.py                # Streamlit custom component wrapper
│   └── voice_composer/         # HTML/JS ChatGPT-style voice widget
│       └── index.html
│
├── data/                       # Persistent storage (auto-created)
│   ├── conversations/          # SQLite database (ai_brain.db)
│   ├── logs/                   # Performance JSONL logs
│   └── voice/                  # Audio recordings
│
├── docs/                       # Technical documentation
│   ├── PROBLEM_STATEMENT.md
│   ├── SYSTEM_ARCHITECTURE.md
│   └── IMPLEMENTATION_PLAN.md
│
└── tests/                      # Verification test suite
    ├── test_cloud.py
    ├── test_connection.py
    ├── test_local.py
    ├── test_memory.py
    ├── test_performance.py
    ├── test_persistence.py
    ├── test_router.py
    ├── test_router_sessions.py
    ├── test_sessions.py
    └── test_voice.py
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- (Optional) [Ollama](https://ollama.com/) for local model fallback:
  ```bash
  ollama run gemma2:2b
  ```

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone <repo-url>
cd AI-Brain
pip install -r requirements.txt
```

### 3. Environment Setup
Create or update `.env` in the root folder:
```ini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:2b
AUTO_SWITCH=true
```

### 4. Running the Streamlit Application
Launch the app with:
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## 🧪 Running Tests

Verify all components individually:
```bash
# Test SQLite Conversation Memory
python -m tests.test_memory

# Test Multi-Session Management
python -m tests.test_sessions

# Test Performance Profiling
python -m tests.test_performance

# Test Router Session Switching
python -m tests.test_router_sessions

# Test Cloud Gemini Connection (requires valid API key & internet)
python -m tests.test_cloud

# Test Local Gemma Connection (requires Ollama running)
python -m tests.test_local
```

---

## 📊 Features & Views

### 1. Chat Interface
- Type prompts or click the microphone to speak.
- Responses show provider badges (`⚡ Answered by: Gemini Cloud` or `⚡ Answered by: Local Gemma`).
- Automatic speech synthesis for voice notes.
- Manage chats from the sidebar (New Chat, Switch, Delete).

### 2. Performance Dashboard
- **System Health:** Live status cards for Cloud API, Local Ollama, SQLite, RAM, and CPU.
- **KPI Metrics:** Total queries, success rate, average latency, and estimated cloud costs.
- **Visual Analytics:** Latency comparison bar chart and RAM usage timeline.
- **Audit Table:** Filterable history of every invocation.

---

## 🛡️ License
MIT License.

