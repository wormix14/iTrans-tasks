from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class BookStat(Base):
    __tablename__ = "book_statistics"
    publication_year: Mapped[int] = mapped_column(primary_key=True)
    book_count: Mapped[int]
    average_price: Mapped[float]