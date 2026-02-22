"""
Fuel Station Ops — Conversational Analytics
Chat-like interface: user types question → gets answer + SQL + data table
"""

import streamlit as st
import pandas as pd
import time
import uuid
from sql_generator import generate_sql
from db import execute_query, log_query, update_feedback

# Approximate cost per token for Claude Sonnet 4 (as of early 2025)
# Input: $3 per 1M tokens, Output: $15 per 1M tokens
INPUT_COST_PER_TOKEN = 3.0 / 1_000_000
OUTPUT_COST_PER_TOKEN = 15.0 / 1_000_000

# Page config
st.set_page_config(
    page_title="Fuel Ops Analytics",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Fuel Station Ops — Conversational Analytics")
st.caption("Ask questions about fuel station operations in plain English — powered by NL→SQL")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "log_ids" not in st.session_state:
    st.session_state.log_ids = {}

# New Conversation button
if st.sidebar.button("🔄 New Conversation"):
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.session_state.session_id = str(uuid.uuid4())[:8]
    st.session_state.feedback = {}
    st.session_state.log_ids = {}
    st.rerun()

# Sidebar with sample questions
st.sidebar.markdown("### Sample Questions")
sample_questions = [
    "Which region has the highest diesel sales this quarter?",
    "Top 5 stations by revenue last month",
    "Average daily footfall — highway vs city stations",
    "Safety incidents in Maharashtra last 3 months",
    "Compare petrol vs diesel volume trends across regions",
    "Which stations are underperforming — below avg revenue but above avg footfall?",
    "Month-over-month growth in total fuel volume",
    "Stations where safety incidents increased vs previous month",
]
for sq in sample_questions:
    if st.sidebar.button(sq, key=sq):
        st.session_state.pending_question = sq
        st.rerun()

# Sidebar footer
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='font-size:0.78rem; color:#888;'>"
    "🤖 Powered by <strong>Claude Sonnet 4</strong><br>"
    "📦 Data: Supabase (PostgreSQL)<br>"
    "🖥️ Frontend: Streamlit<br><br>"
    "Built by <a href='https://www.linkedin.com/in/sandhya-godavarthy-5072622b/' target='_blank'>Sandhya</a>"
    "<br><a href='https://htmlpreview.github.io/?https://github.com/gsandhya31/conv-analyticsmvp1.0/blob/main/product-overview.html' target='_blank'>📄 Product Overview</a>"
    "</div>",
    unsafe_allow_html=True,
)


def render_feedback(msg_index):
    """Render thumbs up/down buttons and persist to DB."""
    col1, col2, col3 = st.columns([0.07, 0.07, 0.86])
    current_feedback = st.session_state.feedback.get(msg_index)

    with col1:
        if st.button(
            "👍" if current_feedback != "up" else "👍✓",
            key=f"up_{msg_index}",
            disabled=current_feedback is not None,
        ):
            st.session_state.feedback[msg_index] = "up"
            # Persist to DB
            log_id = st.session_state.log_ids.get(msg_index)
            update_feedback(log_id, "up")
            st.rerun()
    with col2:
        if st.button(
            "👎" if current_feedback != "down" else "👎✓",
            key=f"down_{msg_index}",
            disabled=current_feedback is not None,
        ):
            st.session_state.feedback[msg_index] = "down"
            # Persist to DB
            log_id = st.session_state.log_ids.get(msg_index)
            update_feedback(log_id, "down")
            st.rerun()
    with col3:
        if current_feedback:
            st.caption("Thanks for the feedback!" if current_feedback == "up" else "Thanks — we'll improve this.")


def render_token_cost(metadata):
    """Show token usage and estimated cost."""
    if not metadata:
        return
    input_t = metadata.get("input_tokens", 0)
    output_t = metadata.get("output_tokens", 0)
    latency = metadata.get("llm_latency_ms", 0)
    cost_usd = (input_t * INPUT_COST_PER_TOKEN) + (output_t * OUTPUT_COST_PER_TOKEN)
    cost_inr = cost_usd * 86  # approx USD to INR
    st.caption(
        f"🔢 Tokens: {input_t} in / {output_t} out &nbsp;|&nbsp; "
        f"💰 ~₹{cost_inr:.4f} &nbsp;|&nbsp; "
        f"⏱️ {latency}ms"
    )


# Display chat history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.write(msg["content"])
        else:
            st.write(msg["answer"])
            if msg.get("assumptions"):
                for a in msg["assumptions"]:
                    st.info(f"📌 Assumption: {a}")
            if msg.get("sql"):
                with st.expander("🔍 View SQL Query"):
                    st.code(msg["sql"], language="sql")
            if msg.get("dataframe") is not None:
                with st.expander(f"📊 View Data ({len(msg['dataframe'])} rows)"):
                    st.dataframe(msg["dataframe"], use_container_width=True)
            if msg.get("metadata"):
                render_token_cost(msg["metadata"])
            render_feedback(i)

st.markdown(
    "<div style='text-align:center; font-size:0.72rem; color:#999; padding:2px 0;'>"
    "⚠️ AI-generated (Claude Sonnet 4) — verify before taking decisions &nbsp;|&nbsp; "
    "Built by <a href='https://www.linkedin.com/in/sandhya-godavarthy-5072622b/' target='_blank' style='color:#f97316;'>Sandhya</a> "
    "&nbsp;|&nbsp; Powered by Claude Sonnet 4 + Supabase + Streamlit"
    "</div>",
    unsafe_allow_html=True,
)

# Handle input
user_input = st.chat_input("Ask a question about fuel station operations...")

if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    start_time = time.time()

    with st.chat_message("assistant"):
        with st.spinner("Analysing your query..."):
            gen = generate_sql(user_input, st.session_state.conversation_history)

        meta = gen.get("metadata", {})
        msg_index = len(st.session_state.messages)  # index for the assistant message we're about to add

        if gen["error"]:
            answer = f"❌ Error generating SQL: {gen['error']}"
            st.error(answer)
            st.session_state.messages.append({"role": "assistant", "answer": answer, "metadata": meta, "assumptions": []})

            elapsed_ms = int((time.time() - start_time) * 1000)
            log_id = log_query(
                session_id=st.session_state.session_id,
                user_question=user_input,
                generated_sql=None,
                explanation=None,
                assumptions=[],
                rows_returned=0,
                execution_time_ms=elapsed_ms,
                sql_valid=False,
                error_message=gen["error"],
                metadata=meta,
            )
            st.session_state.log_ids[msg_index] = log_id
            render_token_cost(meta)
            render_feedback(msg_index)

        elif gen["sql"] is None:
            answer = gen["explanation"]
            st.warning(answer)
            st.session_state.messages.append({"role": "assistant", "answer": answer, "metadata": meta, "assumptions": gen.get("assumptions", [])})

            elapsed_ms = int((time.time() - start_time) * 1000)
            log_id = log_query(
                session_id=st.session_state.session_id,
                user_question=user_input,
                generated_sql=None,
                explanation=gen["explanation"],
                assumptions=gen.get("assumptions", []),
                rows_returned=0,
                execution_time_ms=elapsed_ms,
                sql_valid=True,
                error_message=None,
                metadata=meta,
            )
            st.session_state.log_ids[msg_index] = log_id
            render_token_cost(meta)
            render_feedback(msg_index)

        else:
            st.write(gen["explanation"])

            if gen["assumptions"]:
                for a in gen["assumptions"]:
                    st.info(f"📌 Assumption: {a}")

            with st.expander("🔍 View SQL Query"):
                st.code(gen["sql"], language="sql")

            with st.spinner("Running query..."):
                result = execute_query(gen["sql"])

            df = None
            sql_valid = True
            error_msg = None
            rows_returned = 0

            if result["error"]:
                st.error(f"❌ Query execution error: {result['error']}")
                answer = gen["explanation"]
                sql_valid = False
                error_msg = result["error"]
            elif not result["data"]:
                st.info("📭 No results found for this query.")
                answer = gen["explanation"] + " (No results returned)"
            else:
                df = pd.DataFrame(result["data"])
                rows_returned = len(df)
                with st.expander(f"📊 View Data ({len(df)} rows)"):
                    st.dataframe(df, use_container_width=True)
                answer = gen["explanation"]

            elapsed_ms = int((time.time() - start_time) * 1000)
            log_id = log_query(
                session_id=st.session_state.session_id,
                user_question=user_input,
                generated_sql=gen["sql"],
                explanation=gen["explanation"],
                assumptions=gen.get("assumptions", []),
                rows_returned=rows_returned,
                execution_time_ms=elapsed_ms,
                sql_valid=sql_valid,
                error_message=error_msg,
                metadata=meta,
            )
            st.session_state.log_ids[msg_index] = log_id

            st.session_state.messages.append({
                "role": "assistant",
                "answer": answer,
                "sql": gen["sql"],
                "assumptions": gen.get("assumptions", []),
                "dataframe": df,
                "metadata": meta,
            })

            render_token_cost(meta)
            render_feedback(msg_index)

            summary = ""
            if df is not None:
                summary = f"{len(df)} rows returned. Columns: {list(df.columns)}. First row: {df.iloc[0].to_dict()}" if len(df) > 0 else "Empty result"
            st.session_state.conversation_history.append({
                "question": user_input,
                "sql": gen["sql"],
                "summary": summary,
            })
