import os
import json
from abc import ABC, abstractmethod


class LLMClient(ABC):

    @abstractmethod
    def generate(self, prompt):
        pass


class MockLLMClient(LLMClient):

    def generate(self, prompt):

        # LLM-as-judge request
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

        # Normal chat request
        return (
            "Mock assistant response: "
            "Your shipment can be tracked using your consignment number."
        )


class RealLLMClient(LLMClient):

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

        return response.choices[0].message.content


def get_llm_client():

    provider = os.getenv("LLM_PROVIDER", "mock").lower()

    if provider == "real":
        return RealLLMClient()

    return MockLLMClient()