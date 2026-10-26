import json
from models import BookStat, Base
from session import SessionLocal, engine
from collections import defaultdict
from statistics import mean
import re

Base.metadata.create_all(bind=engine)

def convert_price(price: str) -> float:
    clean = float(re.sub(r'[^\d.]', "", price))
    if "$" not in price:
        return clean * 1.2
    return clean

with open("task1_d.json", "r", encoding="utf-8") as f:
    books = json.load(f)
    statistics = defaultdict(lambda: {"count": 0, "prices": []})
    
for b in books:
    year = b.get("year")
    price = b.get("price")
    statistics[year]["count"] += 1
    statistics[year]["prices"].append(convert_price(price))

with SessionLocal() as db_session: 
    for year, data in statistics.items():   
        avg_price = round(mean(data["prices"]), 2)
        db_session.add(BookStat(
            publication_year=year,
            book_count=data["count"],
            average_price=avg_price,
        ))

    db_session.commit()