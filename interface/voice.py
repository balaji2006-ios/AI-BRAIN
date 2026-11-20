
from pathlib import Path
import streamlit.components.v1 as components


# Locate the custom HTML component
COMPONENT_DIR = (
    Path(__file__).resolve().parent
    / "voice_composer"
)

# Register the custom Streamlit component
voice_composer = components.declare_component(
    "ai_brain_voice_composer",
    path=str(COMPONENT_DIR)
)


def show_voice_composer():
    """
    Display the custom chat composer.

    Returns:
        dict: Text or audio data from the browser.
    """

    return voice_composer(
        key="ai_brain_voice_composer",
        default=None
    )
