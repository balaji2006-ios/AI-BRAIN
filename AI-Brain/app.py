import streamlit as st
import tempfile
import os
import base64

from assistant.router import AIRouter
from assistant.voice.speech_to_text import SpeechToText
from assistant.voice.text_to_speech import TextToSpeech
from interface.dashboard import show_dashboard
from interface.voice import show_voice_composer


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Brain",
    page_icon="🧠",
    layout="wide"
)


# ==========================================
# LOAD SPEECH RECOGNITION
# ==========================================

@st.cache_resource
def load_speech_to_text():
    return SpeechToText()


# Do not cache TTS engine.
# A fresh engine is initialized for each response.
def load_text_to_speech():
    return TextToSpeech()


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_component_event_id" not in st.session_state:
    st.session_state.last_component_event_id = None

if "page" not in st.session_state:
    st.session_state.page = "Chat"


# ==========================================
# INITIALIZE AI ROUTER PER BROWSER SESSION
# ==========================================

if "ai_router" not in st.session_state:

    st.session_state.ai_router = AIRouter(
        session_id=st.session_state.active_session_id
    )

    if st.session_state.active_session_id is None:
        st.session_state.active_session_id = (
            st.session_state.ai_router.memory.session_id
        )

ai = st.session_state.ai_router


# ==========================================
# RESTORE ACTIVE CONVERSATION
# ==========================================

if ai.memory.session_id != st.session_state.active_session_id:

    ai.switch_conversation(
        st.session_state.active_session_id
    )

    st.session_state.messages = ai.memory.get_history()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🧠 AI Brain")

    st.caption("Your Personal AI Assistant")

    st.divider()

    selected_page = st.radio(
        "Navigation",
        ["Chat", "Performance Dashboard"],
        key="navigation"
    )

    st.session_state.page = selected_page

    st.divider()

    if selected_page == "Chat":

        st.subheader("💬 Chat History")

        # ==================================
        # NEW CHAT
        # ==================================

        if st.button(
            "＋ New Chat",
            use_container_width=True
        ):

            new_session_id = ai.new_conversation()

            st.session_state.active_session_id = new_session_id
            st.session_state.messages = []
            st.session_state.last_component_event_id = None

            st.rerun()

        # ==================================
        # LOAD ALL CONVERSATIONS
        # ==================================

        conversations = ai.get_all_conversations()

        if conversations:

            for conversation in conversations:

                session_id = conversation["session_id"]
                title = conversation["title"]

                is_active = (
                    session_id == st.session_state.active_session_id
                )

                col1, col2 = st.columns([5, 1])

                with col1:

                    button_label = (
                        f"🟢 {title}"
                        if is_active
                        else f"💬 {title}"
                    )

                    if st.button(
                        button_label,
                        key=f"chat_{session_id}",
                        use_container_width=True
                    ):

                        ai.switch_conversation(session_id)

                        st.session_state.active_session_id = session_id

                        # Load previous messages from SQLite
                        st.session_state.messages = (
                            ai.memory.get_history()
                        )

                        st.session_state.last_component_event_id = None

                        st.rerun()

                with col2:

                    if st.button(
                        "🗑️",
                        key=f"delete_{session_id}"
                    ):

                        ai.delete_conversation(session_id)

                        # If the active conversation was deleted,
                        # switch to the newly created conversation.
                        if (
                            st.session_state.active_session_id
                            == session_id
                        ):

                            st.session_state.active_session_id = (
                                ai.memory.session_id
                            )

                            st.session_state.messages = []

                            st.session_state.last_component_event_id = None

                        st.rerun()

        else:

            st.caption("No previous conversations.")

        st.divider()

        # ==================================
        # PROVIDER STATUS
        # ==================================

        st.subheader("⚙️ AI Provider")

        provider = ai.current_provider or "Automatic"

        st.info(f"Active provider: {provider}")

        st.caption("Gemini Cloud → Local Gemma fallback")

        st.divider()

        st.caption("Current conversation")

        st.code(
            st.session_state.active_session_id[:12],
            language=None
        )


# ==========================================
# CHAT PAGE
# ==========================================

if st.session_state.page == "Chat":

    st.title("🧠 AI Brain")

    st.caption(
        "Ask questions, learn concepts, write code, "
        "and explore ideas."
    )

    st.divider()

    # ======================================
    # DISPLAY PREVIOUS MESSAGES
    # ======================================

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # ======================================
    # MESSAGE PROCESSING FUNCTION
    # ======================================

    def process_message(prompt, speak_response=False):

        prompt = prompt.strip()

        if not prompt:
            return

        # Display and store user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):

            with st.spinner("AI Brain is thinking..."):

                response = ai.generate_response(prompt)

                st.markdown(response)

                provider = ai.current_provider or "Unknown"

                st.caption(f"Answered by: {provider}")

        # Store assistant response in UI state
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })

        # ==================================
        # TEXT TO SPEECH
        # ==================================

        if speak_response:

            try:

                with st.spinner("🔊 Speaking response..."):

                    tts = load_text_to_speech()

                    tts.speak(response)

            except Exception as error:

                st.warning(
                    f"Text-to-Speech error: {error}"
                )

    # ======================================
    # CHATGPT-STYLE VOICE COMPOSER
    # ======================================

    event = show_voice_composer()

    if event and isinstance(event, dict):

        event_id = event.get("id")

        # Prevent the same component event from
        # being processed again after Streamlit reruns.
        if (
            event_id
            and event_id != st.session_state.last_component_event_id
        ):

            # Mark event before processing
            st.session_state.last_component_event_id = event_id

            event_type = event.get("type")

            # ==================================
            # TYPED MESSAGE
            # ==================================

            if event_type == "text":

                prompt = event.get("text", "").strip()

                if prompt:

                    process_message(
                        prompt,
                        speak_response=False
                    )

                    st.rerun()

            # ==================================
            # VOICE MESSAGE
            # ==================================

            elif event_type == "audio":

                audio_base64 = event.get("audio")

                if not audio_base64:

                    st.error("No audio recording received.")

                else:

                    temp_path = None

                    try:

                        # Decode browser audio
                        audio_bytes = base64.b64decode(
                            audio_base64
                        )

                        mime_type = event.get(
                            "mimeType",
                            "audio/webm"
                        )

                        # Determine audio extension
                        if "wav" in mime_type:
                            suffix = ".wav"

                        elif "ogg" in mime_type:
                            suffix = ".ogg"

                        elif "mp4" in mime_type:
                            suffix = ".mp4"

                        else:
                            suffix = ".webm"

                        # Save audio temporarily
                        with tempfile.NamedTemporaryFile(
                            suffix=suffix,
                            delete=False
                        ) as temp_file:

                            temp_file.write(audio_bytes)

                            temp_path = temp_file.name

                        # ==================================
                        # SPEECH TO TEXT
                        # ==================================

                        with st.spinner(
                            "🎙️ Converting speech to text..."
                        ):

                            stt = load_speech_to_text()

                            result = stt.transcribe(temp_path)

                            prompt = result["text"].strip()

                        if not prompt:

                            st.warning(
                                "No speech detected. Please try again."
                            )

                        else:

                            st.success(
                                f"Recognized speech: {prompt}"
                            )

                            # Voice input always gets spoken output
                            process_message(
                                prompt,
                                speak_response=True
                            )

                            st.rerun()

                    except Exception as error:

                        st.error(
                            f"Voice processing error: {error}"
                        )

                    finally:

                        if (
                            temp_path
                            and os.path.exists(temp_path)
                        ):

                            os.remove(temp_path)


# ==========================================
# PERFORMANCE DASHBOARD
# ==========================================

elif st.session_state.page == "Performance Dashboard":

    st.title("📊 Performance Dashboard")

    st.caption(
        "Monitor response time, RAM usage, "
        "and AI provider performance."
    )

    show_dashboard()
