import sounddevice as sd
from scipy.io.wavfile import write
from assistant.config import VOICE_DIR
from assistant.voice.speech_to_text import SpeechToText
from assistant.voice.text_to_speech import TextToSpeech
from assistant.router import AIRouter


class AudioManager:

    def __init__(self, router=None, sample_rate: int = 16000, duration: int = 7):
        self.sample_rate = sample_rate
        self.duration = duration

        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.router = router if router is not None else AIRouter()

        self.audio_folder = VOICE_DIR
        self.audio_folder.mkdir(parents=True, exist_ok=True)
        self.audio_path = self.audio_folder / "voice_input.wav"

    def record_audio(self) -> str:
        print("\n[AI Brain] Speak now...")
        audio = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
        )
        sd.wait()

        write(str(self.audio_path), self.sample_rate, audio)
        print("[AI Brain] Recording completed.")
        return str(self.audio_path)

    def speech_to_text(self) -> str:
        audio_path = self.record_audio()
        print("[AI Brain] Converting speech to text...")
        result = self.stt.transcribe(audio_path)
        recognized_text = result.get("text", "").strip()
        print("[AI Brain] Recognized:", recognized_text)
        return recognized_text

    def process_voice(self):
        prompt = self.speech_to_text()
        if not prompt:
            print("[AI Brain] No speech detected.")
            return None

        print("\n[AI Brain] Generating response...")
        response = self.router.generate_response(prompt)
        print("\n[AI Brain] AI Response:")
        print(response)

        print("\n[AI Brain] Converting response into speech...")
        self.tts.speak(response)
        return response
