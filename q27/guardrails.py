import re

# Deterministic blocked terms
BANNED_WORDS = [
    "hack",
    "illegal",
    "fraud",
    "weapon",
    "weapons",
    "explosive",
    "explosives",
    "narcotics",
    "mislabel",
]

# Competitor mentions
COMPETITOR_MENTIONS = [
    "competitor1",
    "competitor2",
]

# PII patterns
EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
PHONE_PATTERN = r"\b(?:\+91[- ]?)?[6-9]\d{9}\b"


def check_query(query):
    query_lower = query.lower()

    # 1. Banned keywords
    for word in BANNED_WORDS:
        if word in query_lower:
            return {
                "valid": False,
                "reason": f"Banned keyword detected: {word}"
            }

    # 2. Competitor mentions
    for competitor in COMPETITOR_MENTIONS:
        if competitor in query_lower:
            return {
                "valid": False,
                "reason": f"Competitor mention detected: {competitor}"
            }

    # 3. PII detection
    if re.search(EMAIL_PATTERN, query):
        return {
            "valid": False,
            "reason": "PII detected: email address"
        }

    if re.search(PHONE_PATTERN, query):
        return {
            "valid": False,
            "reason": "PII detected: phone number"
        }

    return {
        "valid": True,
        "reason": "Query passed deterministic guardrail"
    }

import json
from pydantic import BaseModel
from llm_client import get_llm_client


class JudgeResult(BaseModel):
    valid: bool
    reason: str


def llm_policy_check(query):
    try:
        with open("policy/domain.md", "r", encoding="utf-8") as file:
            policy = file.read()

        prompt = f"""
You are a policy judge for Northwind Freight.

POLICY:
{policy}

USER QUERY:
{query}

Decide whether the query is allowed by the policy.

Return ONLY valid JSON in this exact format:
{{
    "valid": true or false,
    "reason": "short explanation"
}}
"""

        client = get_llm_client()
        raw_response = client.generate(prompt)

        data = json.loads(raw_response)
        result = JudgeResult(**data)

        return result.model_dump()

    except Exception as exc:
        # Fail closed: if the judge fails, block the request.
        return {
            "valid": False,
            "reason": f"LLM judge error; request blocked: {exc}"
        }