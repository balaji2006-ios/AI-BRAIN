
import requests
import time

from assistant.config import GEMINI_API_KEY, GEMINI_MODEL

url = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{GEMINI_MODEL}:generateContent"
)

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_API_KEY
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Explain artificial intelligence in 3 simple sentences."}
            ]
        }
    ]
}

print("Testing Gemini text generation...")
print("Model:", GEMINI_MODEL)

start = time.time()

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    print("HTTP Status:", response.status_code)
    print("Time taken:", round(time.time() - start, 2), "seconds")

    response.raise_for_status()

    result = response.json()

    answer = result["candidates"][0]["content"]["parts"][0]["text"]

    print("\nGemini Response:")
    print(answer)

    print("\nText generation successful!")

except requests.exceptions.Timeout:
    print("Request timed out after 30 seconds.")

except requests.exceptions.RequestException as error:
    print("API request failed:", error)
    if error.response is not None:
        print(error.response.text[:1000])

except (KeyError, IndexError, TypeError) as error:
    print("Unexpected API response:", error)

except Exception as error:
    print("Unexpected error:", error)
