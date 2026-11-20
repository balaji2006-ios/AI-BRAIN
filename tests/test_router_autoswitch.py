"""
Test for automatic online/offline routing and seamless fallback in AIRouter.
"""
from assistant.router import AIRouter, check_internet_connection


def test_online_offline_autoswitch():
    print("\n===== TEST: AUTOMATIC ONLINE / OFFLINE SWITCHING =====")

    router = AIRouter(session_id="autoswitch_test")

    # 1. Test live network detection
    online = check_internet_connection(timeout=1.0)
    print(f"Current System State: {'ONLINE' if online else 'OFFLINE'}")

    # 2. Test response generation in current mode
    print("\n--- Phase 1: Automatic Routing (Normal) ---")
    res1 = router.generate_response("Say 'test passed' in 2 words.")
    print("Response:", res1[:100])
    print("Provider used:", router.current_provider)
    assert router.current_provider is not None

    # 3. Test simulated offline switch (cloud disabled)
    print("\n--- Phase 2: Simulated Offline Switch (Forcing Local Fallback) ---")
    router.cloud = None # Cloud disconnected

    res2 = router.generate_response("What is 3+3? Answer with a single digit.")
    print("Response:", res2[:100])
    print("Provider used:", router.current_provider)
    assert "Local" in router.current_provider

    print("\nSUCCESS: Automatic switching between Online and Offline verified!")

    # Clean up test session
    router.memory.clear_history()


if __name__ == "__main__":
    test_online_offline_autoswitch()

