"""
Base provider abstraction for AI Brain models.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class BaseProvider(ABC):
    """
    Abstract base class for all AI Brain model providers (Cloud and Local).
    """

    @abstractmethod
    def generate_response(
        self, prompt: str, history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a text response given a prompt and optional conversation history.

        Args:
            prompt: The user query or message.
            history: List of previous conversation messages with 'role' and 'content'.

        Returns:
            The model's textual response.
        """
        raise NotImplementedError

