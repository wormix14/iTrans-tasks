import sqlite3
import pandas as pd

from .data_loader import load_clean_users, load_clean_orders, load_clean_books

class StoreDatabase:
    def __init__(self, store_dir: str):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.cursor = self.conn.cursor()

        users_df = load_clean_users(store_dir)

        orders_df = load_clean_orders(store_dir)
        orders_df["date"] = orders_df["date"].dt.strftime("%Y-%m-%d")

        books_df = load_clean_books(store_dir)

        orders_df.to_sql("orders", self.conn, if_exists="replace", index=False)
        books_df.to_sql("books", self.conn, if_exists="replace", index=False)
        users_df.to_sql("users", self.conn, if_exists="replace", index=False)

    def execute_query(self, query:str):
        formated_query = query.strip().lower()
        if not formated_query.startswith(("select", "with")):
            return "Error (not select query)"
        try:
            df = pd.read_sql_query(query, self.conn)
            if df.empty:
                return "No data found"
        except Exception as e:
            return f"Database error {e}"
        return df.head(15).to_string(index=False)