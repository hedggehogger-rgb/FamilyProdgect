from datetime import datetime
from typing import Generator
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, create_engine, text,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class FamilyGroupModel(Base):
    __tablename__ = "family_groups"
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserModel(Base):
    __tablename__ = "users"
    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AccountModel(Base):
    __tablename__ = "accounts"
    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)
    balance = Column(Numeric(19, 2), nullable=False, default=0.0)
    is_investment = Column(Boolean, default=False, nullable=False)


class CategoryModel(Base):
    __tablename__ = "categories"
    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    group = Column(String(30), nullable=False)
    periodicity = Column(String(30), nullable=False)
    months_duration = Column(Integer, default=0, nullable=False)
    frequency = Column(String(30), default="NONE", nullable=False)
    day_of_month = Column(Integer, nullable=True)
    day_of_week = Column(Integer, nullable=True)
    recurrence_month = Column(Integer, nullable=True)
    color = Column(String(30), default="#8b5cf6", nullable=False)

    # Новые поля для регулярных операций
    default_amount = Column(Numeric(19, 2), nullable=True)
    default_account_id = Column(String(50), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TransactionModel(Base):
    __tablename__ = "transactions"
    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(50), nullable=True)
    type = Column(String(30), nullable=False)
    amount = Column(Numeric(19, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    account_id = Column(String(50), nullable=False)
    to_account_id = Column(String(50), nullable=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    author = Column(String(20), default="HUSBAND", nullable=False)
    note = Column(String(255), default="", nullable=False)


class CategoryLimitModel(Base):
    __tablename__ = "category_limits"
    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String(50), nullable=False, index=True)
    limit_amount = Column(Numeric(19, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    months_duration = Column(Integer, default=1, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PiggyBankModel(Base):
    __tablename__ = "piggy_banks"
    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), ForeignKey("family_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    target_amount = Column(Numeric(19, 2), nullable=False)
    current_amount = Column(Numeric(19, 2), default=0.0, nullable=False)
    currency = Column(String(10), nullable=False)
    deadline = Column(DateTime, nullable=True)
    account_id = Column(String(50), nullable=False)
    is_auto_replenish = Column(Boolean, default=False, nullable=False)
    auto_replenish_amount = Column(Numeric(19, 2), default=0.0, nullable=False)
    auto_replenish_day = Column(Integer, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PiggyBankNoteModel(Base):
    __tablename__ = "piggy_bank_notes"
    id = Column(String(50), primary_key=True, index=True)
    piggy_bank_id = Column(String(50), ForeignKey("piggy_banks.id", ondelete="CASCADE"), nullable=False)
    author = Column(String(20), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS family_group_id VARCHAR(50);"))
        conn.execute(text("ALTER TABLE accounts ADD COLUMN IF NOT EXISTS family_group_id VARCHAR(50);"))
        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS family_group_id VARCHAR(50);"))
        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS day_of_week INTEGER;"))
        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS recurrence_month INTEGER;"))
        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS color VARCHAR(30) DEFAULT '#8b5cf6';"))
        conn.execute(text("ALTER TABLE category_limits ADD COLUMN IF NOT EXISTS family_group_id VARCHAR(50);"))
        conn.execute(text("ALTER TABLE piggy_banks ADD COLUMN IF NOT EXISTS family_group_id VARCHAR(50);"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS family_group_id VARCHAR(50);"))

        # Добавляем новые колонки для планирования операций
        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS default_amount NUMERIC(19, 2);"))
        conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS default_account_id VARCHAR(50);"))