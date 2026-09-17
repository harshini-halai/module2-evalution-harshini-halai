import os
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()


class LLMClient(ABC):

    @abstractmethod
    def generate(self, prompt):
        pass


class MockLLMClient(LLMClient):

    def generate(self, prompt):

        if "You are a policy judge for Northwind Freight." in prompt:

            if "USER QUERY:" in prompt:
                query = prompt.split("USER QUERY:", 1)[1]
            else:
                query = prompt

            query_lower = query.lower()

            blocked_terms = [
                "ignore the policy",
                "bypass",
                "how to mislabel",
                "mislabel the package",
                "how to ship weapons",
                "how to ship explosives",
                "how to ship narcotics",
                "another customer's shipment",
                "another customer's address",
                "driver identities",
                "backdate delivery records",
            ]

            for term in blocked_terms:
                if term in query_lower:
                    return json.dumps({
                        "valid": False,
                        "reason": f"Policy violation detected: {term}"
                    })

            return json.dumps({
                "valid": True,
                "reason": "Query is allowed under the Northwind Freight policy"
            })

        return (
            "Mock assistant response: "
            "Your shipment can be tracked using your consignment number."
        )


class RealLLMClient(LLMClient):

    def __init__(self):
        self.last_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "cost_usd": 0.0,
        }

    def generate(self, prompt):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=os.getenv(
                "OPENAI_BASE_URL",
                "https://api.openai.com/v1"
            )
        )

        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        prompt_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(response.usage, "completion_tokens", 0) or 0

        prompt_cost = float(
            os.getenv("LLM_PROMPT_COST_PER_1K", "0")
        )
        completion_cost = float(
            os.getenv("LLM_COMPLETION_COST_PER_1K", "0")
        )

        cost_usd = (
            (prompt_tokens / 1000) * prompt_cost
            + (completion_tokens / 1000) * completion_cost
        )

        self.last_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost_usd,
        }

        return response.choices[0].message.content


def get_llm_client():

    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "real":
        return RealLLMClient()

    client = MockLLMClient()

    client.last_usage = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "cost_usd": 0.0,
    }

    return client