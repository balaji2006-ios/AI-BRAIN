from assistant.router import AIRouter


def test_router_sessions():

    print("\n===== AI BRAIN ROUTER SESSION TEST =====")

    # Create first conversation
    ai = AIRouter(session_id="router_test_python")

    ai.memory.add_user_message("Explain Python.")
    ai.memory.add_assistant_message(
        "Python is a programming language."
    )

    print("\nFirst session:", ai.memory.session_id)

    # Create a new conversation
    second_session_id = ai.new_conversation()

    print("\nSecond session:", second_session_id)

    # Check that the new conversation is empty
    assert ai.memory.get_message_count() == 0

    print("New conversation is empty.")

    # Add messages to second conversation
    ai.memory.add_user_message("Explain Java.")
    ai.memory.add_assistant_message(
        "Java is an object-oriented programming language."
    )

    # Switch back to first conversation
    ai.switch_conversation("router_test_python")

    history = ai.memory.get_history()

    print("\nFirst session history:")

    for message in history:
        print(message["role"], ":", message["content"])

    assert len(history) == 2
    assert "Python" in history[0]["content"]

    # Verify second session remains separate
    ai.switch_conversation(second_session_id)

    history = ai.memory.get_history()

    assert len(history) == 2
    assert "Java" in history[0]["content"]

    print("\nSession switching successful!")
    print("Conversation histories are separate.")

    # Clean test messages
    ai.memory.clear_history()

    ai.switch_conversation("router_test_python")
    ai.memory.clear_history()


if __name__ == "__main__":
    test_router_sessions()