from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import extract
from sqlalchemy.orm import Session
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
from app.infrastructure.database import (
    AccountModel,
    CategoryModel,
    SessionLocal,
    TransactionModel,
)


class PostgresAccountRepository(IAccountRepository):

    def save(self, account: Account) -> None:
        db: Session = SessionLocal()
        try:
            model = AccountModel(
                id=account.id,
                name=account.name,
                currency=account.currency.value,
                balance=account.balance,
                is_investment=account.is_investment,
            )
            db.merge(model)
            db.commit()
        finally:
            db.close()

    def find_by_id(self, account_id: str) -> Optional[Account]:
        db: Session = SessionLocal()
        try:
            row = (
                db.query(AccountModel)
                .filter(AccountModel.id == account_id)
                .first()
            )
            return self._to_domain(row) if row else None
        finally:
            db.close()

    def find_all(self) -> List[Account]:
        db: Session = SessionLocal()
        try:
            rows = db.query(AccountModel).all()
            return [self._to_domain(r) for r in rows]
        finally:
            db.close()

    def delete(self, account_id: str) -> bool:
        db: Session = SessionLocal()
        try:
            deleted = (
                db.query(AccountModel)
                .filter(AccountModel.id == account_id)
                .delete()
            )
            db.commit()
            return deleted > 0
        finally:
            db.close()

    @staticmethod
    def _to_domain(row: AccountModel) -> Account:
        return Account(
            id=row.id,
            name=row.name,
            currency=Currency(row.currency),
            balance=Decimal(str(row.balance)),
            is_investment=row.is_investment,
        )


class PostgresCategoryRepository(ICategoryRepository):

    def add(self, category: Category) -> None:
        self.update(category)

    def update(self, category: Category) -> None:
        db: Session = SessionLocal()
        try:
            model = CategoryModel(
                id=category.id,
                name=category.name,
                group=category.group.value,
                periodicity=category.periodicity.value,
                months_duration=category.months_duration,
                frequency=category.frequency.value,
                day_of_month=category.day_of_month,
                created_at=category.created_at,
            )
            db.merge(model)
            db.commit()
        finally:
            db.close()

    def get_by_id(self, category_id: str) -> Optional[Category]:
        db: Session = SessionLocal()
        try:
            row = (
                db.query(CategoryModel)
                .filter(CategoryModel.id == category_id)
                .first()
            )
            return self._to_domain(row) if row else None
        finally:
            db.close()

    def get_all(self) -> List[Category]:
        db: Session = SessionLocal()
        try:
            rows = db.query(CategoryModel).all()
            return [self._to_domain(r) for r in rows]
        finally:
            db.close()

    def delete(self, category_id: str) -> bool:
        db: Session = SessionLocal()
        try:
            deleted = (
                db.query(CategoryModel)
                .filter(CategoryModel.id == category_id)
                .delete()
            )
            db.commit()
            return deleted > 0
        finally:
            db.close()

    @staticmethod
    def _to_domain(row: CategoryModel) -> Category:
        return Category(
            id=row.id,
            name=row.name,
            group=CategoryGroup(row.group),
            periodicity=CategoryPeriodicity(row.periodicity),
            months_duration=row.months_duration,
            frequency=RecurrenceFrequency(row.frequency),
            day_of_month=row.day_of_month,
            created_at=row.created_at,
        )


class PostgresTransactionRepository(ITransactionRepository):

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
                to_account_id=transaction.to_account_id,
                date=transaction.date,
                author=transaction.author.value,
                note=transaction.note,
            )
            db.merge(model)
            db.commit()
        finally:
            db.close()

    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        db: Session = SessionLocal()
        try:
            row = (
                db.query(TransactionModel)
                .filter(TransactionModel.id == transaction_id)
                .first()
            )
            return self._to_domain(row) if row else None
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

    def delete(self, transaction_id: str) -> bool:
        db: Session = SessionLocal()
        try:
            deleted = (
                db.query(TransactionModel)
                .filter(TransactionModel.id == transaction_id)
                .delete()
            )
            db.commit()
            return deleted > 0
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
            to_account_id=row.to_account_id,
            author=Author(row.author),
            note=row.note,
            date=row.date,
        )