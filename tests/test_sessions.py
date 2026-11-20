from assistant.memory.conversation import ConversationMemory


def test_multiple_sessions():

    print("\n===== MULTIPLE SESSION TEST =====")

    # Create first conversation
    session1 = ConversationMemory()
    session1.add_user_message("Explain Python.")
    session1.add_assistant_message("Python is a programming language.")

    # Create second conversation
    session2 = ConversationMemory()
    session2.add_user_message("Explain Java.")
    session2.add_assistant_message("Java is an object-oriented language.")

    # Display session IDs
    print("\nSession 1 ID:", session1.session_id)
    print("Session 2 ID:", session2.session_id)

    # Verify separate histories
    history1 = session1.get_history()
    history2 = session2.get_history()

    print("\nSession 1 History:")
    for message in history1:
        print(message["role"], ":", message["content"])

    print("\nSession 2 History:")
    for message in history2:
        print(message["role"], ":", message["content"])

    # Verify isolation
    assert session1.session_id != session2.session_id
    assert len(history1) == 2
    assert len(history2) == 2

    assert "Python" in history1[0]["content"]
    assert "Java" in history2[0]["content"]

    print("\nTotal Saved Sessions:", len(session1.get_all_sessions()))

    print("\nMultiple Session Test Successful!")

    # Clean up test data
    session1.clear_history()
    session2.clear_history()


if __name__ == "__main__":
    test_multiple_sessions()