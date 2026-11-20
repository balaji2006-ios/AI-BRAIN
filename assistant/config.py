import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=True)

# Gemini Cloud Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Ollama Local Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:latest")

# Automatic Cloud / Local Switching
AUTO_SWITCH = os.getenv("AUTO_SWITCH", "true").lower() in ("true", "1", "yes")

# Database & Storage Directories
DATA_DIR = PROJECT_ROOT / "data"
CONVERSATION_DIR = DATA_DIR / "conversations"
LOGS_DIR = DATA_DIR / "logs"
VOICE_DIR = DATA_DIR / "voice"

for directory in (CONVERSATION_DIR, LOGS_DIR, VOICE_DIR):
    directory.mkdir(parents=True, exist_ok=True)
