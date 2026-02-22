"""
Supabase connection + raw SQL execution + comprehensive query logging.
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def execute_query(sql: str) -> dict:
    """
    Execute a raw SELECT SQL query against Supabase.
    Returns {"data": [...], "error": None} on success,
            {"data": None, "error": "message"} on failure.
    """
    stripped = sql.strip().upper()
    if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
        return {"data": None, "error": "Only SELECT queries are allowed."}

    try:
        result = supabase.rpc("execute_sql", {"query_text": sql}).execute()
        return {"data": result.data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}


def log_query(session_id: str, user_question: str, generated_sql: str,
              explanation: str, assumptions: list, rows_returned: int,
              execution_time_ms: int, sql_valid: bool, error_message: str = None,
              metadata: dict = None) -> int:
    """
    Log every query to the query_logs table.
    Returns the inserted row ID for linking feedback later.
    Fails silently — logging should never break the main flow.
    """
    try:
        row = {
            "session_id": session_id,
            "user_question": user_question,
            "generated_sql": generated_sql,
            "explanation": explanation,
            "assumptions": json.dumps(assumptions) if assumptions else "[]",
            "rows_returned": rows_returned,
            "execution_time_ms": execution_time_ms,
            "sql_valid": sql_valid,
            "error_message": error_message,
        }

        if metadata:
            row["system_prompt"] = None  # too large per-query, stored separately in prompt_versions
            row["request_messages"] = json.dumps(metadata.get("request_messages", []))
            row["raw_llm_response"] = metadata.get("raw_response")
            row["model"] = metadata.get("model")
            row["input_tokens"] = metadata.get("input_tokens", 0)
            row["output_tokens"] = metadata.get("output_tokens", 0)
            row["total_tokens"] = metadata.get("total_tokens", 0)
            row["llm_latency_ms"] = metadata.get("llm_latency_ms", 0)
            row["stop_reason"] = metadata.get("stop_reason")

        result = supabase.table("query_logs").insert(row).execute()
        # Return the ID of the inserted row
        if result.data and len(result.data) > 0:
            return result.data[0].get("id")
        return None
    except Exception as e:
        print(f"Warning: Logging failed: {e}")
        return None


def update_feedback(log_id: int, feedback: str):
    """
    Update the user_feedback column for a specific query log row.
    feedback: "up" or "down"
    """
    if not log_id:
        return
    try:
        supabase.table("query_logs").update(
            {"user_feedback": feedback}
        ).eq("id", log_id).execute()
    except Exception as e:
        print(f"Warning: Feedback update failed: {e}")
