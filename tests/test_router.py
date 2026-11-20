
from assistant.router import AIRouter


def test_router_performance():

    print("\n===== AI BRAIN PERFORMANCE TEST =====")

    ai = AIRouter()

    prompt = "Explain artificial intelligence in simple words."

    print("\nSending prompt to AI Brain...")

    response = ai.generate_response(prompt)

    print("\nAI Response:")
    print(response)

    print("\nPerformance Results:")

    results = ai.get_performance_history()

    for result in results:

        print("Provider:", result["provider"])
        print("Status:", result["status"])
        print("Response Time:", result["response_time"], "seconds")
        print("RAM Before:", result["ram_before_mb"], "MB")
        print("RAM After:", result["ram_after_mb"], "MB")
        print("RAM Change:", result["ram_change_mb"], "MB")


if __name__ == "__main__":
    test_router_performance()
