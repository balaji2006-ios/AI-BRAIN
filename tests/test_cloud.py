
from assistant.providers.cloud_gemini import GeminiProvider


def test_gemini_connection():
    print("\nConnecting to Gemini API...")

    try:
        gemini = GeminiProvider()

        question = "Explain artificial intelligence in simple words."

        print("\nQuestion:", question)

        response = gemini.generate_response(question)

        print("\nGemini Response:")
        print(response)

        print("\nGemini API test successful!")

    except Exception as error:
        print("\nGemini API test failed!")
        print("Error:", error)


if __name__ == "__main__":
    test_gemini_connection()
