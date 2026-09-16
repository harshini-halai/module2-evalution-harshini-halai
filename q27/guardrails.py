import re

BANNED_WORDS = [
    "hack",
    "illegal",
    "fraud"
]

COMPETITOR_MENTIONS = [
    "competitor1",
    "competitor2"
]

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
