# Implementation Plan & Workflow Guide

## Workflows & Data Flows

### 1. User Message Flow (Text)
1. The user enters text into the chat input or custom composer.
2. The UI appends the user's message to `st.session_state.messages` and displays it immediately in the chat feed.
3. `AIRouter.generate_response(prompt)` is called:
   - Recent messages are fetched from SQLite via `ConversationMemory` and trimmed by `ContextManager`.
   - `PerformanceMonitor.start_tracking()` logs initial timestamp and RAM RSS.
   - `GeminiProvider` sends the payload over HTTPS to Google Generative Language API.
   - If successful, the response text is returned.
   - If an error occurs (network unreachable, quota exhausted, invalid key), `GemmaProvider` forwards the payload to local Ollama (`/api/chat`).
   - SQLite tables `conversations` and `messages` are updated with the exchange.
   - Metrics (latency, RAM shift, tokens, estimated USD cost) are calculated and written to `data/logs/performance.jsonl`.
4. Streamlit displays the assistant's reply with provider attribution.

### 2. Voice Input & Output Flow
1. The user clicks the microphone button in the custom voice composer (`index.html`).
2. Browser `navigator.mediaDevices.getUserMedia` captures audio chunks and builds a `Blob`.
3. When stopped, audio is base64-encoded and sent to Streamlit via `window.parent.postMessage`.
4. `interface/chat.py` receives the base64 payload and writes it to a temporary audio file.
5. `SpeechToText.transcribe()` invokes `faster-whisper` (or falls back to `SpeechRecognition`) to convert the audio into text.
6. The transcribed query flows into the standard `AIRouter.generate_response()` pipeline.
7. Upon receiving the assistant's response, `TextToSpeech.speak()` synthesizes voice output via `pyttsx3`.

### 3. Monitoring & Health Auditing Flow
1. The user selects **Performance Dashboard** from the sidebar radio.
2. `interface/dashboard.py` calls `health_check.run_full_health_check()`:
   - Tests Gemini API connectivity (`ping()`).
   - Tests local Ollama server status and model availability.
   - Inspects SQLite database integrity.
   - Reads system RAM and CPU utilization from `psutil`.
3. Loads records from `data/logs/performance.jsonl` into a Pandas DataFrame.
4. Renders operational KPIs, provider comparison bar chart, memory timeline, and searchable interaction logs.

