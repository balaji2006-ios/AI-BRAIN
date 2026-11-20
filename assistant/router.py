import socket
from typing import Optional, List, Dict, Any
from assistant.providers.cloud_gemini import GeminiProvider
from assistant.providers.local_gemma import GemmaProvider
from assistant.memory.conversation import ConversationMemory
from assistant.memory.context_manager import ContextManager
from assistant.evaluation.performance import PerformanceMonitor
from assistant.evaluation.cost_tracker import CostTracker


def check_internet_connection(timeout: float = 1.2) -> bool:
    """
    Rapidly determines if the system has active internet access.
    Takes <0.05s when online, <=1.2s when offline.
    """
    try:
        sock = socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        sock.close()
        return True
    except OSError:
        return False


class AIRouter:

    def __init__(self, session_id: Optional[str] = None):
        self.cloud: Optional[GeminiProvider] = None
        self.local: Optional[GemmaProvider] = None

        try:
            self.cloud = GeminiProvider()
        except Exception as err:
            print(f"[AI Brain] Gemini Cloud initialization skipped: {err}")

        try:
            self.local = GemmaProvider()
        except Exception as err:
            print(f"[AI Brain] Local Ollama initialization skipped: {err}")

        self.memory = ConversationMemory(session_id=session_id)
        self.context_manager = ContextManager(max_messages=10)
        self.performance_monitor = PerformanceMonitor()

        self.current_provider: Optional[str] = None
        self.last_error: Optional[str] = None
        self.performance_history: List[Dict[str, Any]] = []

    def get_network_status(self) -> Dict[str, Any]:
        """Returns live connectivity status and default provider."""
        online = check_internet_connection(timeout=1.0)
        default_provider = "Gemini Cloud" if (online and self.cloud is not None) else "Local Gemma"
        return {
            "online": online,
            "status_label": "🟢 Online (Gemini Cloud)" if online else "🟠 Offline (Local Gemma)",
            "default_provider": default_provider,
        }

    # =================================
    # CONVERSATION MANAGEMENT
    # =================================

    def new_conversation(self) -> str:
        self.memory = ConversationMemory()
        print("[AI Brain] New conversation created:", self.memory.session_id)
        return self.memory.session_id

    def switch_conversation(self, session_id: str):
        self.memory = ConversationMemory(session_id=session_id)
        print("[AI Brain] Switched to conversation:", session_id)

    def get_all_conversations(self) -> List[Dict[str, Any]]:
        return self.memory.get_all_sessions()

    def delete_conversation(self, session_id: str):
        self.memory.delete_session(session_id)
        if self.memory.session_id == session_id:
            self.new_conversation()
        print("[AI Brain] Conversation deleted:", session_id)

    def clear_conversation(self):
        self.memory.clear_history()
        print("[AI Brain] Current conversation cleared.")

    # =================================
    # AUTOMATIC ONLINE / OFFLINE ROUTING
    # =================================

    def generate_response(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        conversation_history = self.memory.get_history()
        context_window = self.context_manager.get_context(conversation_history)

        answer = None
        provider = None
        errors = []

        self.performance_monitor.start_tracking()

        # Step 1: Detect active internet connectivity in <0.1s
        online = check_internet_connection(timeout=1.2)

        try:
            # Case A: System is ONLINE and Gemini Cloud is configured
            if online and self.cloud is not None:
                try:
                    print("\n[AI Brain] Status: ONLINE. Querying Gemini Cloud...")
                    answer = self.cloud.generate_response(prompt, context_window)
                    provider = "Gemini Cloud"
                    print("[AI Brain] Success with Gemini Cloud")
                except Exception as cloud_err:
                    self.last_error = str(cloud_err)
                    errors.append(f"Cloud Gemini failed: {cloud_err}")
                    print(f"[AI Brain] Cloud failure ({cloud_err}). Auto-switching to Local Ollama fallback...")

            # Case B: System is OFFLINE
            elif not online:
                print("\n[AI Brain] Status: OFFLINE. Automatically routing to Local Ollama with zero delay...")
                errors.append("System is offline (no internet access).")

            # Case C: Cloud unconfigured
            else:
                errors.append("Gemini Cloud provider unconfigured.")

            # Step 2: Automatic Fallback / Offline routing to Local Ollama
            if answer is None:
                if self.local is not None:
                    try:
                        print("[AI Brain] Generating response with Local Ollama...")
                        answer = self.local.generate_response(prompt, context_window)
                        provider = "Local Gemma (Offline Mode)" if not online else "Local Gemma (Cloud Fallback)"
                        print(f"[AI Brain] Success with {provider}")
                    except Exception as local_err:
                        errors.append(f"Local Ollama failed: {local_err}")
                        raise RuntimeError(
                            "Automatic AI routing failed on all engines:\n• " + "\n• ".join(errors)
                        )
                else:
                    raise RuntimeError(
                        "System is offline or cloud failed, and Local Ollama is unavailable:\n• " + "\n• ".join(errors)
                    )

            self.current_provider = provider
            self.last_error = None

            # Persist exchange to SQLite memory
            self.memory.add_user_message(prompt)
            self.memory.add_assistant_message(answer)

            return answer

        finally:
            metrics = self.performance_monitor.stop_tracking()
            metrics["provider"] = provider or "Failed"
            metrics["status"] = "Success" if answer is not None else "Failed"
            metrics["session_id"] = self.memory.session_id
            metrics["mode"] = "Online" if online else "Offline"

            # Cost estimation (Cloud costs vs $0.00 local)
            if answer is not None:
                pricing_provider = "Gemini Cloud" if "Gemini" in metrics["provider"] else "Local Gemma"
                cost_info = CostTracker.calculate_cost(pricing_provider, prompt, answer)
                metrics.update(cost_info)

            self.performance_history.append(metrics)
            self.performance_monitor.save_record(metrics)

            print("\n[AI Brain] Performance Metrics:")
            print("Mode:", metrics["mode"])
            print("Provider:", metrics["provider"])
            print("Response Time:", metrics["response_time"], "seconds")
            print("RAM Change:", metrics["ram_change_mb"], "MB")

    # =================================
    # PERFORMANCE HISTORY
    # =================================

    def get_performance_history(self) -> List[Dict[str, Any]]:
        return self.performance_history

    def get_all_performance_records(self) -> List[Dict[str, Any]]:
        return self.performance_monitor.get_all_records()
