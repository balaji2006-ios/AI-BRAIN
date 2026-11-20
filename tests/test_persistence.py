from assistant.router import AIRouter


ai = AIRouter()

print("\n===== AI BRAIN PERSISTENCE TEST =====")

history = ai.memory.get_history()

print("\nPreviously saved conversation:")

if history:
    for message in history[-4:]:
        print(
            message["role"].upper(),
            ":",
            message["content"][:150]
        )
else:
    print("No previous conversation found.")

print("\nTotal messages:", ai.memory.get_message_count())