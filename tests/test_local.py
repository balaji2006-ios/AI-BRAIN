
from assistant.providers.local_gemma import GemmaProvider


def test_local_gemma():

    print("\nConnecting to local Gemma...")

    try:
        gemma = GemmaProvider()

        question = "Explain artificial intelligence in simple words."

        print("\nQuestion:", question)

        response = gemma.generate_response(question)

        print("\nGemma Response:")
        print(response)

        print("\nLocal Gemma test successful!")

    except Exception as error:
        print("\nLocal Gemma test failed!")
        print("Error:", error)


if __name__ == "__main__":
    test_local_gemma()
