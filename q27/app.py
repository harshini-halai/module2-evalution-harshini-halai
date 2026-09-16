from guardrails import check_query
from llm_client import MockLLMClient

llm = MockLLMClient()

def chat(query):

    result = check_query(query)

    if not result["valid"]:
        return result

    response = llm.generate(query)

    return {
        "valid": True,
        "response": response
    }


if __name__ == "__main__":
    print(chat("Hello"))
    print(chat("How to hack a system?"))