# Problem Statement: AI Brain

## 1. Background
Modern AI applications heavily rely on either purely cloud-based API services (e.g., OpenAI, Google Cloud Gemini) or purely local on-device inference models (e.g., Ollama running Gemma or Llama). 

Both extremes suffer from significant drawbacks:
- **Cloud-Only Solutions:** Require continuous internet connectivity, incur API costs, introduce privacy concerns for sensitive discussions, and suffer catastrophic failure if external APIs or network connections experience downtime.
- **Local-Only Solutions:** Bound by device hardware constraints (RAM, CPU/GPU capacity), slower generation speed on non-specialized hardware, and may struggle with complex conceptual reasoning compared to large-scale cloud foundation models.

## 2. Objective
**AI Brain** bridges this gap by designing an intelligent, adaptive hybrid AI assistant that seamlessly combines:
1. **Cloud Intelligence (Primary):** Leverages Google Gemini for fast, state-of-the-art conversational reasoning.
2. **Local Fallback (Secondary):** Automatically falls back to local models (Gemma via Ollama) when internet connectivity is severed, rate limits are reached, or API failures occur.
3. **Persistent SQLite Memory:** Retains multi-turn conversational context and session state across reloads.
4. **Voice Interaction Loop:** Provides hands-free ChatGPT-style voice input (Speech-to-Text) and spoken output (Text-to-Speech).
5. **System & Cost Observability:** Tracks latency, RAM footprint, token usage, and financial cost via an interactive Streamlit Performance Dashboard.

## 3. Success Metrics
- **Zero Downtime Routing:** Graceful degradation from cloud to local without dropping conversation context or crashing the user interface.
- **Persistent Multi-Session Memory:** Users can switch, resume, and manage multiple chat histories stored reliably in SQLite.
- **Low Latency & Minimal Memory Overhead:** Real-time metrics tracking ensures resource usage remains transparent to the user.
- **Accessible UI:** A responsive, interactive Streamlit frontend supporting typed queries and voice recording.

