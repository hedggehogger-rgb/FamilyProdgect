from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
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


class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)
    balance = Column(Numeric(19, 2), nullable=False, default=0.0)
    is_investment = Column(Boolean, default=False, nullable=False)


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    group = Column(String(30), nullable=False)
    periodicity = Column(String(30), nullable=False)
    months_duration = Column(Integer, default=0, nullable=False)
    frequency = Column(String(30), default="NONE", nullable=False)
    day_of_month = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String(50), primary_key=True, index=True)
    category_id = Column(
        String(50), nullable=True
    )  # Для переводов может быть null
    type = Column(String(30), nullable=False)
    amount = Column(Numeric(19, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    account_id = Column(String(50), nullable=False)  # Счёт списания
    to_account_id = Column(
        String(50), nullable=True
    )  # Счёт пополнения (для переводов)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    author = Column(String(20), default="HUSBAND", nullable=False)
    note = Column(String(255), default="", nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)