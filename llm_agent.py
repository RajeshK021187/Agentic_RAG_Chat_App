import re
import subprocess
from db_utils import run_query  
SCHEMA_INFO = """
You are connected to a MySQL database named `federal_register`.

The database contains a single table: `documents`.

The `documents` table has the following columns:
- id (INT): Primary key
- document_number (VARCHAR): Unique document identifier
- title (TEXT): Title of the document
- doc_type (VARCHAR): Type of the document (e.g., Presidential Document, Notice)
- publication_date (DATE): Date when the document was published

Your job is to convert natural language questions into safe SQL queries for this schema. Return ONLY the SQL query inside triple backticks (```) with no explanation.
"""

def run_llm_agent(user_question: str) -> str:
    prompt = f"""
{SCHEMA_INFO}

User question:
{user_question}

Respond with the SQL query to answer the question, inside triple backticks.
"""

    # Call Ollama
    result = subprocess.run(
        ["ollama", "run", "mistral", prompt],
        capture_output=True,
        text=True
    )
    raw_output = result.stdout

    # Extract SQL query
    sql_match = re.search(r"```(?:sql)?\s*(.*?)```", raw_output, re.DOTALL)
    if not sql_match:
        return "Sorry, I couldn't understand the request."

    sql_query = sql_match.group(1).strip()

    try:
        rows = run_query(sql_query)
        if not rows:
            return "No results found."

        headers = [desc[0] for desc in rows.description]
        values = rows.fetchall()

        # Simplify output:

        # If only 1 column and 1 row => return that value as string
        if len(headers) == 1 and len(values) == 1:
            return str(values[0][0])

        # Else if multiple rows and one column => return comma-separated values
        if len(headers) == 1:
            return ", ".join(str(row[0]) for row in values)

        # Else (multiple columns or rows) => format each row as a comma-separated string, join by newline
        result_strings = []
        for row in values:
            row_str = ", ".join(str(col) for col in row)
            result_strings.append(row_str)
        return "\n".join(result_strings)

    except Exception as e:
        return f"Error executing SQL: {str(e)}"
