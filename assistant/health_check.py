"""
System health checks for AI Brain components.
"""
import psutil
from typing import Dict, Any
from assistant.config import GEMINI_API_KEY, GEMINI_MODEL, OLLAMA_BASE_URL, OLLAMA_MODEL, CONVERSATION_DIR
from assistant.providers.cloud_gemini import GeminiProvider
from assistant.providers.local_gemma import GemmaProvider
from assistant.memory.conversation import ConversationMemory


def check_gemini_health() -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        return {
            "status": "unconfigured",
            "message": "Gemini API key is not set in .env",
            "model": GEMINI_MODEL,
        }
    try:
        provider = GeminiProvider()
        reachable = provider.ping()
        return {
            "status": "healthy" if reachable else "unreachable",
            "message": "Connected to Gemini Cloud" if reachable else "Gemini API endpoint unreachable (check network)",
            "model": provider.model,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "model": GEMINI_MODEL,
        }


def check_ollama_health() -> Dict[str, Any]:
    try:
        provider = GemmaProvider()
        reachable = provider.ping()
        models = provider.list_installed_models() if reachable else []
        model_installed = any(provider.model in m for m in models) if models else False
        return {
            "status": "healthy" if (reachable and model_installed) else ("warning" if reachable else "offline"),
            "message": f"Ollama is online ({len(models)} models available)" if reachable else "Ollama server offline",
            "configured_model": provider.model,
            "model_ready": model_installed,
            "installed_models": models,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "configured_model": OLLAMA_MODEL,
        }


def check_database_health() -> Dict[str, Any]:
    try:
        mem = ConversationMemory(session_id="__health_check__")
        mem.create_table()
        count = mem.get_message_count()
        return {
            "status": "healthy",
            "message": f"SQLite database connected ({count} messages in health check session)",
            "db_path": str(mem.db_path),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"SQLite error: {e}",
        }


def check_system_resources() -> Dict[str, Any]:
    try:
        vm = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)
        return {
            "status": "healthy",
            "ram_total_gb": round(vm.total / (1024 ** 3), 1),
            "ram_used_gb": round(vm.used / (1024 ** 3), 1),
            "ram_percent": vm.percent,
            "cpu_percent": cpu,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }


def run_full_health_check() -> Dict[str, Any]:
    return {
        "gemini": check_gemini_health(),
        "ollama": check_ollama_health(),
        "database": check_database_health(),
        "resources": check_system_resources(),
    }

