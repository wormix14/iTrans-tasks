import pandas as pd
import matplotlib.pyplot as plt
from .data_loader import load_clean_orders

def process_orders(store_dir: str):
    orders_df = load_clean_orders(store_dir)

    # computing daily revenue
    daily_revenue = orders_df.groupby("date")["paid_price"].sum()
    top_5_days = daily_revenue.sort_values(ascending=False).head(5)
    top_5_days.index = top_5_days.index.strftime("%Y-%m-%d")

    #creating linechart
    fig = plt.figure(figsize=(14, 6))
    daily_revenue_chart = orders_df.groupby(orders_df["date"].dt.date)["paid_price"].sum().sort_index()
    plt.plot(daily_revenue_chart.index, daily_revenue_chart.values)
    plt.xlabel("date")
    plt.ylabel("revenue")

    plt.gcf().autofmt_xdate()

    return top_5_days, fig