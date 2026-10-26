from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL="postgresql+psycopg2://postgres:postgres120306@localhost:5432/iTransition_db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False)
