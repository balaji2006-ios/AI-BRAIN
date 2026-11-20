import streamlit as st

from assistant.router import AIRouter
from interface.chat import render_chat_page
from interface.dashboard import show_dashboard


# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Brain - Intelligent Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


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

# Initialize AI Router per browser session
if "ai_router" not in st.session_state:
    st.session_state.ai_router = AIRouter(
        session_id=st.session_state.active_session_id
    )
    if st.session_state.active_session_id is None:
        st.session_state.active_session_id = (
            st.session_state.ai_router.memory.session_id
        )

ai = st.session_state.ai_router

# Synchronize active conversation session
if ai.memory.session_id != st.session_state.active_session_id:
    ai.switch_conversation(st.session_state.active_session_id)
    st.session_state.messages = ai.memory.get_history()


# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.title("🧠 AI Brain")
    st.caption("Dual Online/Offline AI Assistant")

    st.divider()

    selected_page = st.radio(
        "Navigation",
        ["Chat", "Performance Dashboard"],
        key="navigation",
    )
    st.session_state.page = selected_page

    st.divider()

    if selected_page == "Chat":
        st.subheader("💬 Conversations")

        # Create New Chat
        if st.button("＋ New Conversation", use_container_width=True, type="primary"):
            new_session_id = ai.new_conversation()
            st.session_state.active_session_id = new_session_id
            st.session_state.messages = []
            st.session_state.last_component_event_id = None
            st.rerun()

        st.write("")

        # List Existing Conversations
        conversations = ai.get_all_conversations()
        if conversations:
            for conversation in conversations:
                session_id = conversation["session_id"]
                title = conversation["title"]
                is_active = session_id == st.session_state.active_session_id

                col1, col2 = st.columns([5, 1])
                with col1:
                    label = f"🟢 {title}" if is_active else f"💬 {title}"
                    if st.button(label, key=f"chat_{session_id}", use_container_width=True):
                        ai.switch_conversation(session_id)
                        st.session_state.active_session_id = session_id
                        st.session_state.messages = ai.memory.get_history()
                        st.session_state.last_component_event_id = None
                        st.rerun()

                with col2:
                    if st.button("🗑️", key=f"del_{session_id}", help="Delete chat"):
                        ai.delete_conversation(session_id)
                        if st.session_state.active_session_id == session_id:
                            st.session_state.active_session_id = ai.memory.session_id
                            st.session_state.messages = []
                            st.session_state.last_component_event_id = None
                        st.rerun()
        else:
            st.caption("No conversations yet.")

        st.divider()

        # Dynamic Online / Offline Status
        st.subheader("⚙️ Routing Engine")
        net_info = ai.get_network_status()
        st.info(f"**Status:** {net_info['status_label']}\n\n**Provider:** {ai.current_provider or net_info['default_provider']}")
        st.caption("Auto-Switch: Gemini Cloud (Online) ⇄ Local Gemma (Offline)")

        st.caption(f"Session: `{str(st.session_state.active_session_id)[:8]}...`")


# ==========================================
# PAGE ROUTING
# ==========================================
if st.session_state.page == "Chat":
    render_chat_page(ai)
elif st.session_state.page == "Performance Dashboard":
    show_dashboard()
