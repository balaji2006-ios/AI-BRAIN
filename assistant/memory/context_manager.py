
class ContextManager:
    """
    Manages conversation history sent to Gemini and Gemma.
    """

    def __init__(self, max_messages=10):
        self.max_messages = max_messages

    def get_context(self, history):
        """
        Returns the most recent messages within the context limit.
        """

        if not history:
            return []

        return history[-self.max_messages:]

    def clear_context(self):
        """
        Reset context limit to its default value.
        """

        self.max_messages = 10

    def update_context_limit(self, new_limit):
        """
        Update the maximum number of messages to retain.
        """

        if new_limit < 1:
            raise ValueError("Context limit must be at least 1.")

        self.max_messages = new_limit
