"""
Cost tracking and token estimation for AI Brain queries.
"""
from typing import Dict, Any, List


class CostTracker:
    """
    Estimates token counts and costs for LLM requests.
    Gemini 2.5/1.5 Flash pricing:
    - Input: $0.075 / 1,000,000 tokens ($0.000000075 / token)
    - Output: $0.30 / 1,000,000 tokens ($0.00000030 / token)
    Local Gemma: $0.00 (Free)
    """

    PRICING = {
        "Gemini Cloud": {
            "input_per_million": 0.075,
            "output_per_million": 0.30,
        },
        "Local Gemma": {
            "input_per_million": 0.0,
            "output_per_million": 0.0,
        },
    }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Heuristic estimation of tokens (~4 chars per token)."""
        if not text:
            return 0
        return max(1, int(len(text) / 4))

    @classmethod
    def calculate_cost(
        cls, provider: str, prompt: str, response: str
    ) -> Dict[str, Any]:
        input_tokens = cls.estimate_tokens(prompt)
        output_tokens = cls.estimate_tokens(response)
        total_tokens = input_tokens + output_tokens

        pricing = cls.PRICING.get(provider, {"input_per_million": 0.075, "output_per_million": 0.30})
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_million"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_million"]
        total_cost = input_cost + output_cost

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost_usd": round(total_cost, 7),
        }

    @classmethod
    def calculate_total_cost(cls, records: List[Dict[str, Any]]) -> float:
        total = 0.0
        for r in records:
            if r.get("status") == "Success":
                cost = r.get("cost_usd", 0.0)
                total += cost
        return round(total, 6)

