"""
NL→SQL generator using Claude API.
Takes a user question, sends it with schema context to Claude, gets SQL back.
Returns full metadata for logging (tokens, latency, raw response, etc.)
"""

import os
import json
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from prompts import SYSTEM_PROMPT, build_prompt

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"


def generate_sql(user_question: str, conversation_history: list = None) -> dict:
    """
    Send user question to Claude API, get back SQL + explanation + full metadata.
    Returns dict with keys: sql, explanation, assumptions, error, metadata
    """
    messages = build_prompt(user_question, conversation_history)

    metadata = {
        "system_prompt": SYSTEM_PROMPT,
        "request_messages": messages,
        "raw_response": None,
        "model": MODEL,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "llm_latency_ms": 0,
        "stop_reason": None,
    }

    try:
        start = time.time()
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        metadata["llm_latency_ms"] = int((time.time() - start) * 1000)

        # Capture token usage
        metadata["input_tokens"] = response.usage.input_tokens
        metadata["output_tokens"] = response.usage.output_tokens
        metadata["total_tokens"] = response.usage.input_tokens + response.usage.output_tokens
        metadata["stop_reason"] = response.stop_reason

        # Extract text from response
        raw_text = response.content[0].text.strip()
        metadata["raw_response"] = raw_text

        # Parse JSON — handle cases where Claude wraps it in markdown code fences
        clean_text = raw_text
        if clean_text.startswith("```"):
            clean_text = clean_text.split("```")[1]
            if clean_text.startswith("json"):
                clean_text = clean_text[4:]
            clean_text = clean_text.strip()

        result = json.loads(clean_text)

        return {
            "sql": result.get("sql"),
            "explanation": result.get("explanation", ""),
            "assumptions": result.get("assumptions", []),
            "error": None,
            "metadata": metadata,
        }

    except json.JSONDecodeError:
        # Claude responded conversationally instead of JSON — treat as non-SQL answer
        return {
            "sql": None,
            "explanation": raw_text[:500],
            "assumptions": [],
            "error": None,
            "metadata": metadata,
        }
    except Exception as e:
        return {
            "sql": None,
            "explanation": "",
            "assumptions": [],
            "error": f"Claude API error: {str(e)}",
            "metadata": metadata,
        }


# Quick test
if __name__ == "__main__":
    q = "Which region has the highest diesel sales this quarter?"
    print(f"Q: {q}\n")
    result = generate_sql(q)
    if result["error"]:
        print(f"ERROR: {result['error']}")
    else:
        print(f"SQL: {result['sql']}")
        print(f"Explanation: {result['explanation']}")
    m = result["metadata"]
    print(f"\n--- Metadata ---")
    print(f"Model: {m['model']}")
    print(f"Input tokens: {m['input_tokens']}")
    print(f"Output tokens: {m['output_tokens']}")
    print(f"Total tokens: {m['total_tokens']}")
    print(f"LLM latency: {m['llm_latency_ms']}ms")
    print(f"Stop reason: {m['stop_reason']}")
