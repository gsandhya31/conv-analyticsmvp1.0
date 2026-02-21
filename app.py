"""
Fuel Operations Conversational Analytics — Streamlit Frontend
Chat-like interface: user types question → gets answer + SQL + data table
"""

import streamlit as st
import pandas as pd
import time
import uuid
from sql_generator import generate_sql
from db import execute_query, log_query

# Page config
st.set_page_config(
    page_title="Fuel Ops Analytics",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Fuel Station Ops — Conversational Analytics")
st.caption("Ask questions about fuel station operations in plain English  — powered by NL→SQL")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

# New Conversation button
if st.sidebar.button("🔄 New Conversation"):
    st.session_state.messages = []
    st.session_state.conversation_history = []
    st.session_state.session_id = str(uuid.uuid4())[:8]
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

# Display chat history
for msg in st.session_state.messages:
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

# Handle input — either from chat box or sidebar button
user_input = st.chat_input("Ask a question about - fuel station operations...")

if "pending_question" in st.session_state:
    user_input = st.session_state.pending_question
    del st.session_state.pending_question

if user_input:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Track total time
    start_time = time.time()

    # Process
    with st.chat_message("assistant"):
        with st.spinner("Analysing your query..."):
            gen = generate_sql(user_input, st.session_state.conversation_history)

        meta = gen.get("metadata", {})

        if gen["error"]:
            answer = f"❌ Error generating SQL: {gen['error']}"
            st.error(answer)
            st.session_state.messages.append({"role": "assistant", "answer": answer})

            elapsed_ms = int((time.time() - start_time) * 1000)
            log_query(
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

        elif gen["sql"] is None:
            answer = gen["explanation"]
            st.warning(answer)
            st.session_state.messages.append({"role": "assistant", "answer": answer})

            elapsed_ms = int((time.time() - start_time) * 1000)
            log_query(
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

        else:
            # Show explanation
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
            log_query(
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

            st.session_state.messages.append({
                "role": "assistant",
                "answer": answer,
                "sql": gen["sql"],
                "assumptions": gen.get("assumptions", []),
                "dataframe": df,
            })

            summary = ""
            if df is not None:
                summary = f"{len(df)} rows returned. Columns: {list(df.columns)}. First row: {df.iloc[0].to_dict()}" if len(df) > 0 else "Empty result"
            st.session_state.conversation_history.append({
                "question": user_input,
                "sql": gen["sql"],
                "summary": summary,
            })
