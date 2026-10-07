from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Numeric,
    String,
    create_engine,
    extract,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String(50), primary_key=True, index=True)
    category_id = Column(String(50), nullable=False)
    type = Column(String(30), nullable=False)
    amount = Column(Numeric(19, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    account_id = Column(String(50), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    author = Column(String(20), default="HUSBAND", nullable=False)
    note = Column(String(255), default="", nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)