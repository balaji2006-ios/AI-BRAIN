"""
Unified Chat Interface for AI Brain.
Combines typing and voice interactions into ONE single unified ChatGPT-style input bar.
"""
import os
import base64
import tempfile
import streamlit as st

from assistant.voice.speech_to_text import SpeechToText
from assistant.voice.text_to_speech import TextToSpeech
from interface.voice import show_voice_composer


@st.cache_resource
def get_speech_to_text():
    return SpeechToText()


def get_text_to_speech():
    return TextToSpeech()


def render_chat_page(ai):
    """
    Renders the unified conversational interface for AI Brain.
    """
    st.title("🧠 AI Brain")
    st.caption("Ask questions, explore concepts, brainstorm, or chat by voice.")

    # Top options: simple audio playback toggle
    col1, col2 = st.columns([5, 1])
    with col2:
        voice_playback = st.toggle("🔊 Audio TTS", value=True, help="Read answers aloud with Text-to-Speech")

    st.divider()

    # Ensure messages list exists in session state
    if "messages" not in st.session_state:
        st.session_state.messages = ai.memory.get_history()

    # Display conversation message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ----------------------------------------------------
    # Unified Message Processor
    # ----------------------------------------------------
    def process_message(prompt: str, speak_response: bool = False):
        prompt = prompt.strip()
        if not prompt:
            return

        # Record user message in UI
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate Assistant response
        with st.chat_message("assistant"):
            with st.spinner("AI Brain is thinking..."):
                try:
                    response = ai.generate_response(prompt)
                    st.markdown(response)
                    provider = ai.current_provider or "AI Brain"
                    st.caption(f"⚡ Answered by: {provider}")

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                    })

                    # Optional Text-to-Speech synthesis
                    if speak_response and voice_playback:
                        try:
                            with st.spinner("🔊 Speaking response..."):
                                tts = get_text_to_speech()
                                tts.speak(response)
                        except Exception as tts_err:
                            st.warning(f"Voice playback warning: {tts_err}")

                except Exception as error:
                    error_msg = f"⚠️ Could not generate response: {error}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })

    # ----------------------------------------------------
    # ONE SINGLE UNIFIED COMPOSER (Text + Voice in one bar)
    # ----------------------------------------------------
    event = show_voice_composer()

    if event and isinstance(event, dict):
        event_id = event.get("id")

        if event_id and event_id != st.session_state.get("last_component_event_id"):
            st.session_state.last_component_event_id = event_id
            event_type = event.get("type")

            # 1. Clean transcribed text (from typing or real-time Web Speech mic)
            if event_type in ("message", "text"):
                prompt_text = event.get("text", "").strip()
                is_voice = bool(event.get("is_voice", False))

                if prompt_text:
                    if is_voice:
                        st.info(f"🎙️ **Recognized voice query:** *\"{prompt_text}\"*")
                    process_message(prompt_text, speak_response=is_voice)
                    st.rerun()

            # 2. Raw audio fallback (transcribed by Faster-Whisper on backend)
            elif event_type in ("audio_blob", "audio"):
                audio_base64 = event.get("audio")
                if audio_base64:
                    temp_path = None
                    try:
                        audio_bytes = base64.b64decode(audio_base64)
                        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as temp_file:
                            temp_file.write(audio_bytes)
                            temp_path = temp_file.name

                        with st.spinner("🎙️ Transcribing voice note..."):
                            stt = get_speech_to_text()
                            result = stt.transcribe(temp_path)
                            recognized_prompt = result.get("text", "").strip()

                        if recognized_prompt:
                            st.info(f"🎙️ **Recognized voice query:** *\"{recognized_prompt}\"*")
                            process_message(recognized_prompt, speak_response=True)
                            st.rerun()
                        else:
                            st.warning("No speech detected. Please try speaking again.")

                    except Exception as err:
                        st.error(f"Voice transcription error: {err}")
                    finally:
                        if temp_path and os.path.exists(temp_path):
                            try:
                                os.remove(temp_path)
                            except Exception:
                                pass
