from services.orders_service import process_orders
from services.books_service import process_books
from services.users_service import process_users



def analyze_store(store_dir: str):
    orders_df, top_5_days, chart_fig = process_orders(store_dir)

    author_set_count, most_sold_authors = process_books(store_dir, orders_df)

    unique_users_count, best_ids, best_name = process_users(store_dir, orders_df)

    return {
        "top_5_days": top_5_days,
        "unique_users_count": unique_users_count,
        "author_set_count": author_set_count,
        "most_sold_authors": most_sold_authors,
        "best_ids": best_ids,
        "best_name" : best_name,
        "chart_fig": chart_fig
    }