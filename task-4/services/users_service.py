import pandas as pd
import os
from collections import defaultdict
from .data_loader import load_clean_users, load_clean_orders

def process_users(store_dir: str):
    users_df = load_clean_users(store_dir)
    orders_df = load_clean_orders(store_dir)

    # counting unique users
    parent = {}
    for id in users_df["id"]:
        parent[id] = id

    def find_parent_id(id):
        while parent[id] != id:
            id = parent[id]
        return id

    def union(a, b):
        a_parent = find_parent_id(a)
        b_parent = find_parent_id(b)
        if a_parent != b_parent:
            parent[a_parent] = b_parent

    combinations = [
        ["name", "address", "phone"],
        ["name", "address", "email"],
        ["name", "phone", "email"],
        ["address", "phone", "email"]
    ]

    for comb in combinations:
        valid_mask = users_df[comb].notna().all(axis=1)
        sub_df = users_df[valid_mask]

        has_dup = sub_df.duplicated(subset=comb, keep=False)
        dup_df = sub_df[has_dup]
        duplicate_ids = dup_df.groupby(comb)["id"].apply(list)

        for id_lst in duplicate_ids:
            for id in id_lst[1:]:
                union(id_lst[0], id)

    unique_users_count = len(set(find_parent_id(p) for p in parent.keys()))

    # finding the most profit user 
    merged_users = orders_df.merge(users_df, left_on="user_id", right_on="id", how="inner")
    user_amounts = merged_users.groupby("user_id")["paid_price"].sum().sort_values(ascending=False)

    unique_users_amounts = defaultdict(float)

    for user, amount in user_amounts.items():
        unique_users_amounts[find_parent_id(user)] += amount

    max_val = max(unique_users_amounts.values())
    best_users = set([k for k, v in unique_users_amounts.items() if v == max_val])

    best_ids = [id for id in parent.keys() if find_parent_id(id) in best_users]

    best_names_series = users_df[users_df["id"].isin(best_ids)]["name"].dropna().unique()
    best_name = " / ".join(best_names_series) if len(best_names_series) > 0 else "Unknown"

    return unique_users_count, best_ids, best_name