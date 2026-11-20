from assistant.memory.conversation import ConversationMemory


def test_memory_persistence():

    print("\n===== SQLITE MEMORY TEST =====")

    # Create a separate test session
    memory = ConversationMemory(
        session_id="persistence_test"
    )

    # Save messages
    memory.add_user_message(
        "My name is Balaji."
    )

    memory.add_assistant_message(
        "Hello Balaji! Nice to meet you."
    )

    print("\nMessages saved successfully.")

    # Create another memory object
    new_memory = ConversationMemory(
        session_id="persistence_test"
    )

    # Retrieve saved messages
    history = new_memory.get_history()

    print("\nRetrieved Conversation:")

    for message in history:
        print(message["role"], ":", message["content"])

    print("\nTotal Messages:", new_memory.get_message_count())

    # Verify persistence
    assert len(history) == 2

    print("\nSQLite Persistence Test Successful!")

    # Clean up test session
    new_memory.clear_history()


if __name__ == "__main__":
    test_memory_persistence()