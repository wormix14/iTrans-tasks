import os
import yaml
import pandas as pd

def load_clean_orders(store_dir: str) -> pd.DataFrame:
    orders_df = pd.read_parquet(os.path.join(store_dir, "orders.parquet"))

    orders_df["shipping"] = orders_df["shipping"].replace(['', 'NULL'], pd.NA)
    orders_df = orders_df.replace(r"^\s*$", pd.NA, regex=True)
    orders_df = orders_df.drop_duplicates()

    is_eur = orders_df["unit_price"].str.contains(r"EUR|eur|€", na=False)

    orders_df["unit_price"] = (
        orders_df["unit_price"]
        .str.replace(r"(\d)[€¢](\d)", r"\1.\2", regex=True)
        .str.replace(r"[^\d.]", "", regex=True)
        .astype(float)
    )

    orders_df.loc[is_eur, "unit_price"] *= 1.2

    orders_df["date"] = (
        orders_df["timestamp"]
        .str.replace(r"[,;]", " ", regex=True)
        .str.replace("P.M.", "PM")
        .str.replace("A.M.", "AM")
    )

    orders_df["date"] = pd.to_datetime(orders_df["date"], format="mixed").dt.normalize()

    orders_df = orders_df.drop_duplicates().reset_index(drop=True)

    # adding new column
    orders_df["paid_price"] = (orders_df["quantity"] * orders_df["unit_price"]).round(2)

    return orders_df

def load_clean_books(store_dir: str) -> pd.DataFrame:
    """Загружает books.yaml, убирает двоеточия из колонок, чистит NULL и пустые строки."""
    with open(os.path.join(store_dir, "books.yaml"), "r", encoding="utf-8") as f:
        books_raw = yaml.safe_load(f)
    
    df = pd.DataFrame(books_raw)
    df.columns = [c.lstrip(":") for c in df.columns]
    df = df.replace(["NULL", "None", "null"], pd.NA).replace(r"^\s*$", pd.NA, regex=True)

    return df

def load_clean_users(store_dir: str) -> pd.DataFrame:
    """Загружает users.csv, удаляет пробельные строки и дубликаты."""
    df = pd.read_csv(os.path.join(store_dir, "users.csv"))
    df = df.replace(r"^\s*$", pd.NA, regex=True).drop_duplicates()
    return df