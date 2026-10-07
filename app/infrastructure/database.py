from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
    extract,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from app.core.config import settings

engine = create_engine(settings.DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# --- НОВЫЕ ТАБЛИЦЫ: СЕМЬЯ И ПОЛЬЗОВАТЕЛИ ---


class FamilyGroupModel(Base):
    __tablename__ = "family_groups"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(
        String(50),
        ForeignKey("family_groups.id", ondelete="CASCADE"),
        nullable=False,
    )
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        String(20), nullable=False
    )  # HUSBAND, WIFE или другое отображаемое имя
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


# --- СУЩЕСТВУЮЩИЕ ТАБЛИЦЫ ---


class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), nullable=True)  # Привязка к семье
    name = Column(String(100), nullable=False)
    currency = Column(String(10), nullable=False)
    balance = Column(Numeric(19, 2), nullable=False, default=0.0)
    is_investment = Column(Boolean, default=False, nullable=False)


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String(50), primary_key=True, index=True)
    family_group_id = Column(String(50), nullable=True)  # Привязка к семье
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
    category_id = Column(String(50), nullable=False, index=True)
    limit_amount = Column(Numeric(19, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    months_duration = Column(Integer, default=1, nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PiggyBankModel(Base):
    __tablename__ = "piggy_banks"

    id = Column(String(50), primary_key=True, index=True)
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
    piggy_bank_id = Column(
        String(50),
        ForeignKey("piggy_banks.id", ondelete="CASCADE"),
        nullable=False,
    )
    author = Column(String(20), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)