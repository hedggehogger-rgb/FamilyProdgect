from datetime import datetime
from decimal import Decimal
import json
import os
import threading
from typing import Dict, List, Optional
from sqlalchemy import extract
from sqlalchemy.orm import Session
from app.core.config import settings
from app.domain.interfaces import (
    IAccountRepository,
    ICategoryRepository,
    ITransactionRepository,
)
from app.domain.models import (
    Account,
    Author,
    Category,
    CategoryGroup,
    CategoryPeriodicity,
    Currency,
    RecurrenceFrequency,
    Transaction,
    TransactionType,
)
from app.infrastructure.database import SessionLocal, TransactionModel


class InMemoryAccountRepository(IAccountRepository):

    def __init__(self):
        self._storage: Dict[str, Account] = {}
        self._lock = threading.Lock()

    def save(self, account: Account) -> None:
        with self._lock:
            self._storage[account.id] = account

    def find_by_id(self, account_id: str) -> Optional[Account]:
        with self._lock:
            return self._storage.get(account_id)

    def find_all(self) -> List[Account]:
        with self._lock:
            return list(self._storage.values())


class InMemoryCategoryRepository(ICategoryRepository):

    def __init__(self):
        self._storage: Dict[str, Category] = {}
        self._lock = threading.Lock()

    def add(self, category: Category) -> None:
        with self._lock:
            self._storage[category.id] = category

    def get_by_id(self, category_id: str) -> Optional[Category]:
        with self._lock:
            return self._storage.get(category_id)

    def get_all(self) -> List[Category]:
        with self._lock:
            return list(self._storage.values())


class JsonFileTransactionRepository(ITransactionRepository):

    def __init__(self, file_path: str = settings.STORAGE_FILE_PATH):
        self._file_path = file_path
        self._lock = threading.Lock()

    def _load(self) -> List[Transaction]:
        if not os.path.exists(self._file_path):
            return []
        with open(self._file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [
                Transaction(
                    id=item["id"],
                    type=TransactionType(item["type"]),
                    category_id=item["category_id"],
                    amount=Decimal(item["amount"]),
                    currency=Currency(item["currency"]),
                    account_id=item["account_id"],
                    author=Author(item["author"]),
                    note=item["note"],
                    date=datetime.fromisoformat(item["date"]),
                )
                for item in data
            ]

    def _dump(self, transactions: List[Transaction]) -> None:
        payload = [
            {
                "id": t.id,
                "type": t.type.value,
                "category_id": t.category_id,
                "amount": str(t.amount),
                "currency": t.currency.value,
                "account_id": t.account_id,
                "author": t.author.value,
                "note": t.note,
                "date": t.date.isoformat(),
            }
            for t in transactions
        ]
        with open(self._file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

    def save(self, transaction: Transaction) -> None:
        with self._lock:
            txs = self._load()
            txs.append(transaction)
            self._dump(txs)

    def get_all(self) -> List[Transaction]:
        with self._lock:
            return self._load()

    def get_by_period(self, year: int, month: int) -> List[Transaction]:
        with self._lock:
            return [
                tx
                for tx in self._load()
                if tx.date.year == year and tx.date.month == month
            ]


class PostgresTransactionRepository(ITransactionRepository):

    def __init__(self):
        pass

    def save(self, transaction: Transaction) -> None:
        db: Session = SessionLocal()
        try:
            model = TransactionModel(
                id=transaction.id,
                type=transaction.type.value,
                category_id=transaction.category_id,
                amount=transaction.amount,
                currency=transaction.currency.value,
                account_id=transaction.account_id,
                date=transaction.date,
                author=transaction.author.value,
                note=transaction.note,
            )
            db.merge(model)
            db.commit()
        finally:
            db.close()

    def get_all(self) -> List[Transaction]:
        db: Session = SessionLocal()
        try:
            rows = db.query(TransactionModel).all()
            return [self._to_domain(r) for r in rows]
        finally:
            db.close()

    def get_by_period(self, year: int, month: int) -> List[Transaction]:
        db: Session = SessionLocal()
        try:
            # Фильтрация прямо на уровне базы данных PostgreSQL
            rows = (
                db.query(TransactionModel)
                .filter(
                    extract("year", TransactionModel.date) == year,
                    extract("month", TransactionModel.date) == month,
                )
                .all()
            )
            return [self._to_domain(r) for r in rows]
        finally:
            db.close()

    @staticmethod
    def _to_domain(row: TransactionModel) -> Transaction:
        return Transaction(
            id=row.id,
            type=TransactionType(row.type),
            category_id=row.category_id,
            amount=Decimal(str(row.amount)),
            currency=Currency(row.currency),
            account_id=row.account_id,
            author=Author(row.author),
            note=row.note,
            date=row.date,
        )