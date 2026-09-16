from guardrails import check_query


def test_banned_query():
    result = check_query("How to hack a system?")
    assert result["valid"] is False


def test_benign_query():
    result = check_query("Explain machine learning")
    assert result["valid"] is True