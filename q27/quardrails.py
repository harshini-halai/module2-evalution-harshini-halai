BANNED_WORDS = ["hack", "illegal"]

def check_query(query):
    query_lower = query.lower()

    for word in BANNED_WORDS:
        if word in query_lower:
            return {
                "valid": False,
                "reason": "Banned keyword detected"
            }

    return {
        "valid": True,
        "reason": "Query allowed"
    }