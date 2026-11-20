
from assistant.voice.audio_manager import AudioManager
from assistant.router import AIRouter

print("\n========== AI BRAIN VOICE ASSISTANT ==========")

# Create shared AI Router
router = AIRouter()

# Initialize voice assistant
assistant = AudioManager(router=router)

print("\nAI Brain is ready. Ask your question!")

# Complete voice interaction
response = assistant.process_voice()

print("\n========== FINAL RESULT ==========")

if response:
    print("Provider:", router.current_provider)
    print("Response:", response)

print("\nVoice interaction completed!")
