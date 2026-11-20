import requests
from typing import List, Dict, Optional
from assistant.config import GEMINI_API_KEY, GEMINI_MODEL
from assistant.providers.base import BaseProvider


class GeminiProvider(BaseProvider):
    """
    Google Gemini Cloud AI provider utilizing the Generative Language REST API.
    """

    FALLBACK_MODELS = [
        "gemini-3.5-flash",
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-3-flash-preview",
    ]

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or GEMINI_MODEL

        if not self.api_key:
            raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY in your .env file.")

        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

    def _get_url(self, model_name: str) -> str:
        clean_name = model_name.replace("models/", "")
        return f"{self.base_url}/{clean_name}:generateContent"

    def ping(self) -> bool:
        """Quick check to see if Gemini API is reachable with the current credentials."""
        try:
            url = f"{self.base_url}?key={self.api_key}"
            res = requests.get(url, timeout=5)
            return res.status_code == 200
        except Exception:
            return False

    def generate_response(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        contents = []
        for message in history or []:
            role = message.get("role", "user")
            if role == "assistant":
                role = "model"

            contents.append({
                "role": role,
                "parts": [{"text": message.get("content", "")}],
            })

        contents.append({
            "role": "user",
            "parts": [{"text": prompt.strip()}],
        })

        payload = {"contents": contents}

        # Try active model first, then fallbacks
        models_to_try = [self.model] + [m for m in self.FALLBACK_MODELS if m != self.model]

        last_error = None
        for model_name in models_to_try:
            try:
                url = self._get_url(model_name)
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30,
                )

                # Retry on 404 (model deprecated/not found), 503 (high demand), or 429 (rate limit)
                if response.status_code in (404, 503, 429):
                    last_error = f"Model {model_name} returned HTTP {response.status_code} ({response.text[:120]})."
                    print(f"[AI Brain] {last_error} Retrying with next model...")
                    continue

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Gemini API error {response.status_code}: {response.text[:300]}"
                    )

                result = response.json()
                candidates = result.get("candidates", [])
                if not candidates:
                    raise RuntimeError("Gemini returned an empty candidate list.")

                content_obj = candidates[0].get("content", {})
                parts = content_obj.get("parts", [])
                if not parts:
                    raise RuntimeError("Gemini returned a response with no text parts.")

                answer = parts[0].get("text", "")
                self.model = model_name
                return answer.strip()

            except requests.exceptions.Timeout:
                last_error = f"Gemini model {model_name} timed out."
                print(f"[AI Brain] {last_error} Retrying...")
                continue
            except requests.exceptions.ConnectionError:
                raise RuntimeError("Unable to connect to Gemini API. Check your internet connection.")
            except Exception as e:
                last_error = str(e)
                raise

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")
