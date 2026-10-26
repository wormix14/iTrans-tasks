import os
from dotenv import load_dotenv
from openai import OpenAI
from services.db_service import StoreDatabase

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

MODEL = "openai/gpt-oss-120b"

SCHEMA = """
Tables (SQLite):
- orders(id INT, user_id INT, book_id INT, quantity INT, unit_price REAL, paid_price REAL, shipping TEXT, date TEXT 'YYYY-MM-DD')
- books(id INT, title TEXT, author TEXT, genre TEXT, price REAL)
- users(id INT, name TEXT, address TEXT, phone TEXT, email TEXT)
"""


def ask_assistant(user_message: str, db: StoreDatabase, chat_history: list = None) -> str:
    sql_res = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"You are a SQLite expert. {SCHEMA}\nReturn ONLY a raw SQLite SELECT query. No markdown, no explanations.",
            },
            {"role": "user", "content": user_message},
        ],
        temperature=0.0,
    )

    sql = sql_res.choices[0].message.content

    db_result = db.execute_query(sql)

    final_res = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a bookstore analytics assistant. Answer clearly and concisely based strictly on the SQL result.",
            },
            {
                "role": "user",
                "content": f"Question: {user_message}\nSQL: {sql}\nResult:\n{db_result}",
            },
        ],
        temperature=0.2,
    )

    return final_res.choices[0].message.content