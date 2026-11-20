"""
Speech-to-Text module supporting Faster-Whisper and SpeechRecognition fallback.
"""
from typing import Dict, Any, Optional
import os


class SpeechToText:

    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self._model = None
        self._use_whisper = True

    def _get_whisper_model(self):
        if self._model is None and self._use_whisper:
            try:
                print(f"[AI Brain] Loading Whisper model ({self.model_size})...")
                from faster_whisper import WhisperModel
                self._model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )
                print("[AI Brain] Whisper model loaded successfully!")
            except Exception as e:
                print(f"[AI Brain] Faster-Whisper unavailable: {e}. Falling back to SpeechRecognition.")
                self._use_whisper = False
        return self._model

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        if not audio_path or not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # 1. Try Faster-Whisper first
        whisper_model = self._get_whisper_model()
        if whisper_model is not None:
            try:
                segments, info = whisper_model.transcribe(
                    audio_path,
                    language="en",
                    beam_size=5
                )
                text = " ".join(segment.text.strip() for segment in segments)
                return {
                    "text": text.strip(),
                    "language": info.language,
                    "language_probability": info.language_probability,
                    "engine": "faster-whisper",
                }
            except Exception as e:
                print(f"[AI Brain] Whisper transcription failed: {e}. Trying fallback...")

        # 2. Fallback to SpeechRecognition (Google Web Speech)
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return {
                    "text": text.strip(),
                    "language": "en",
                    "language_probability": 1.0,
                    "engine": "google-speech-recognition",
                }
        except Exception as sr_err:
            raise RuntimeError(
                f"Speech transcription failed with all engines: {sr_err}"
            )
