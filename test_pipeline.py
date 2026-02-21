"""
End-to-end test: user question → Claude generates SQL → execute on Supabase → print results.
Run this to verify the full pipeline works before building the frontend.
"""

from sql_generator import generate_sql
from db import execute_query


def ask(question: str):
    print(f"\n{'='*60}")
    print(f"Q: {question}")

    # Step 1: Generate SQL
    gen = generate_sql(question)
    if gen["error"]:
        print(f"❌ Generation error: {gen['error']}")
        return

    if gen["sql"] is None:
        print(f"⚠️  Cannot answer: {gen['explanation']}")
        return

    print(f"📝 SQL: {gen['sql']}")
    print(f"💡 Explanation: {gen['explanation']}")
    if gen["assumptions"]:
        print(f"🔍 Assumptions: {gen['assumptions']}")

    # Step 2: Execute SQL
    result = execute_query(gen["sql"])
    if result["error"]:
        print(f"❌ Execution error: {result['error']}")
        return

    # Step 3: Display results
    data = result["data"]
    if not data:
        print("📭 No results returned.")
        return

    print(f"✅ {len(data)} row(s) returned:")
    for row in data[:10]:  # show first 10
        print(f"   {row}")


if __name__ == "__main__":
    questions = [
        '''
 "Compare petrol vs diesel volume trends across regions",
    "Which stations are underperforming — below average revenue but above average footfall?",
    "What's the month-over-month growth in total fuel volume?",
    "Show me stations where safety incidents increased compared to previous month",
    '''
    "tell me why the safety incidents have increased in the past 3 months?"
    ]

    for q in questions:
        ask(q)
