import pandas as pd
from .data_loader import load_clean_books, load_clean_orders

def process_books(store_dir: str):
    
    books_df = load_clean_books(store_dir)
    orders_df = load_clean_orders(store_dir)


    # counting unique sets of authors
    books_df["author"] = books_df["author"].dropna().apply(
        lambda a: frozenset(name.strip() for name in a.split(","))
    )

    author_set_count = books_df["author"].dropna().nunique()

    # finding the most sold author
    merged_books = orders_df.merge(books_df, left_on="book_id", right_on="id", how="inner")
    author_sales = merged_books.groupby("author")["quantity"].sum().sort_values(ascending=False)
    
    # if many authors
    max_sold_val = author_sales.max()
    most_sold_authors = [
        ", ".join(list(a_set)) 
        for a_set, q in author_sales.items() 
        if q == max_sold_val
    ]
    return author_set_count, most_sold_authors