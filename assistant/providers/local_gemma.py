import requests
from typing import List, Dict, Optional
from assistant.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from assistant.providers.base import BaseProvider


class GemmaProvider(BaseProvider):
    """
    Local Ollama AI provider supporting Gemma, Qwen, and any installed Ollama model.
    Runs 100% offline on-device.
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")
        self.model = model or OLLAMA_MODEL
        self.chat_url = f"{self.base_url}/api/chat"

    def ping(self) -> bool:
        """Quick check to see if Ollama server is running and accessible."""
        try:
            res = requests.get(f"{self.base_url}/api/version", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def list_installed_models(self) -> List[str]:
        """Fetch list of models available in the local Ollama instance."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", [])]
            return []
        except Exception:
            return []

    def _resolve_model(self) -> str:
        """Select the best installed local model."""
        installed = self.list_installed_models()
        if not installed:
            return self.model

        # Priority resolution: Configured model -> gemma2:2b -> qwen3:latest -> first installed
        for candidate in [self.model, "gemma2:2b", "qwen3:latest"]:
            for m in installed:
                if m == candidate or m.startswith(candidate + ":"):
                    return m

        return installed[0]

    def generate_response(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        active_model = self._resolve_model()

        system_prompt = (
            "You are AI Brain, a helpful, intelligent, and concise AI assistant running offline.\n\n"
            "RESPONSE RULES:\n"
            "1. Answer the exact question directly.\n"
            "2. Keep answers short and clear (2 to 4 sentences).\n"
            "3. For explanations, use concise bullet points.\n"
            "4. Prioritize correctness and brevity."
        )

        messages = [{"role": "system", "content": system_prompt}]

        for message in history or []:
            role = message.get("role")
            content = message.get("content", "")
            if role in ("user", "assistant") and content.strip():
                messages.append({"role": role, "content": content})

        messages.append({"role": "user", "content": prompt.strip()})

        payload = {
            "model": active_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.4,
                "num_predict": 256,
            },
        }

        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                timeout=180,
            )
            response.raise_for_status()
            result = response.json()

            message = result.get("message") or {}
            answer = message.get("content", "")

            if not isinstance(answer, str) or not answer.strip():
                raise RuntimeError(
                    f"Local model ({active_model}) returned an empty response. Details: {result}"
                )

            self.model = active_model
            return answer.strip()

        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to local Ollama server at {self.base_url}. Make sure Ollama is running."
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Local model ({active_model}) timed out after 180 seconds.")
        except requests.exceptions.HTTPError as error:
            status = getattr(error.response, "status_code", None)
            if status == 404:
                raise RuntimeError(
                    f"Model '{active_model}' not found in Ollama. Pull it with: ollama pull {active_model}"
                )
            raise RuntimeError(f"Ollama API error: {error}")
        except requests.exceptions.RequestException as error:
            raise RuntimeError(f"Ollama request failed: {error}")
