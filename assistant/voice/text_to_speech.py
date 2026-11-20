"""
Text-to-Speech module using pyttsx3.
"""
from typing import Optional


class TextToSpeech:

    def __init__(self, rate: int = 175, volume: float = 1.0):
        self.rate = rate
        self.volume = volume
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            import pyttsx3
            # Initialize engine fresh
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", self.rate)
            self.engine.setProperty("volume", self.volume)
            print("[AI Brain] Text-to-Speech initialized.")
        except Exception as e:
            print(f"[AI Brain] Text-to-Speech initialization warning: {e}")
            self.engine = None

    def speak(self, text: str):
        if not text or not text.strip():
            print("[AI Brain] Nothing to speak.")
            return

        if self.engine is None:
            self._init_engine()

        if self.engine is None:
            print("[AI Brain] TTS engine unavailable; skipping voice synthesis.")
            return

        try:
            print("[AI Brain] Speaking response...")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[AI Brain] Speech synthesis failed: {e}")
