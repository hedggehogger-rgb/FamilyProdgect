from contextlib import contextmanager
from decimal import Decimal
from typing import Generator, List, Optional, Tuple
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


class BasePostgresRepository:
    def __init__(self, db: Optional[Session] = None):
        self._db = db

    @contextmanager
    def _get_db(self) -> Generator[Session, None, None]:
        if self._db is not None:
            yield self._db
        else:
            session: Session = SessionLocal()
            try:
                yield session
            finally:
                session.close()


class PostgresAccountRepository(BasePostgresRepository, IAccountRepository):

    def save(self, account: Account) -> None:
        with self._get_db() as db:
            model = AccountModel(
                id=account.id,
                family_group_id=account.family_group_id,
                name=account.name,
                currency=account.currency.value,
                balance=account.balance,
                is_investment=account.is_investment,
            )
            db.merge(model)
            db.commit()

    def find_by_id(
        self, account_id: str, family_group_id: Optional[str] = None
    ) -> Optional[Account]:
        with self._get_db() as db:
            q = db.query(AccountModel).filter(AccountModel.id == account_id)
            if family_group_id:
                q = q.filter(AccountModel.family_group_id == family_group_id)
            row = q.first()
            return self._to_domain(row) if row else None

    def find_all(self, family_group_id: Optional[str] = None) -> List[Account]:
        with self._get_db() as db:
            q = db.query(AccountModel)
            if family_group_id:
                q = q.filter(AccountModel.family_group_id == family_group_id)
            return [self._to_domain(r) for r in q.all()]

    def delete(
        self, account_id: str, family_group_id: Optional[str] = None
    ) -> bool:
        with self._get_db() as db:
            q = db.query(AccountModel).filter(AccountModel.id == account_id)
            if family_group_id:
                q = q.filter(AccountModel.family_group_id == family_group_id)
            deleted = q.delete()
            db.commit()
            return deleted > 0

    @staticmethod
    def _to_domain(row: AccountModel) -> Account:
        return Account(
            id=row.id,
            name=row.name,
            currency=Currency(row.currency),
            balance=Decimal(str(row.balance)),
            is_investment=row.is_investment,
            family_group_id=row.family_group_id,
        )


class PostgresCategoryRepository(BasePostgresRepository, ICategoryRepository):

    def add(self, category: Category) -> None:
        self.update(category)

    def update(self, category: Category) -> None:
        with self._get_db() as db:
            model = CategoryModel(
                id=category.id,
                family_group_id=category.family_group_id,
                name=category.name,
                group=category.group.value,
                periodicity=category.periodicity.value,
                months_duration=category.months_duration,
                frequency=category.frequency.value,
                day_of_month=category.day_of_month,
                day_of_week=category.day_of_week,
                recurrence_month=category.recurrence_month,
                color=category.color,
                created_at=category.created_at,
            )
            db.merge(model)
            db.commit()

    def get_by_id(
        self, category_id: str, family_group_id: Optional[str] = None
    ) -> Optional[Category]:
        with self._get_db() as db:
            q = db.query(CategoryModel).filter(CategoryModel.id == category_id)
            if family_group_id:
                q = q.filter(CategoryModel.family_group_id == family_group_id)
            row = q.first()
            return self._to_domain(row) if row else None

    def get_all(self, family_group_id: Optional[str] = None) -> List[Category]:
        with self._get_db() as db:
            q = db.query(CategoryModel)
            if family_group_id:
                q = q.filter(CategoryModel.family_group_id == family_group_id)
            return [self._to_domain(r) for r in q.all()]

    def delete(
        self, category_id: str, family_group_id: Optional[str] = None
    ) -> bool:
        with self._get_db() as db:
            q = db.query(CategoryModel).filter(CategoryModel.id == category_id)
            if family_group_id:
                q = q.filter(CategoryModel.family_group_id == family_group_id)
            deleted = q.delete()
            db.commit()
            return deleted > 0

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
            day_of_week=getattr(row, "day_of_week", None),
            recurrence_month=getattr(row, "recurrence_month", None),
            color=getattr(row, "color", "#8b5cf6") or "#8b5cf6",
            family_group_id=row.family_group_id,
            created_at=row.created_at,
        )


class PostgresTransactionRepository(
    BasePostgresRepository, ITransactionRepository
):

    def save(self, transaction: Transaction) -> None:
        with self._get_db() as db:
            model = TransactionModel(
                id=transaction.id,
                family_group_id=transaction.family_group_id,
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

    def get_by_id(
        self, transaction_id: str, family_group_id: Optional[str] = None
    ) -> Optional[Transaction]:
        with self._get_db() as db:
            q = db.query(TransactionModel).filter(
                TransactionModel.id == transaction_id
            )
            if family_group_id:
                q = q.filter(
                    TransactionModel.family_group_id == family_group_id
                )
            row = q.first()
            return self._to_domain(row) if row else None

    def get_all(
        self, family_group_id: Optional[str] = None
    ) -> List[Transaction]:
        with self._get_db() as db:
            q = db.query(TransactionModel)
            if family_group_id:
                q = q.filter(
                    TransactionModel.family_group_id == family_group_id
                )
            rows = q.order_by(TransactionModel.date.desc()).all()
            return [self._to_domain(r) for r in rows]

    def get_paginated(
        self,
        family_group_id: str,
        limit: int = 50,
        offset: int = 0,
        account_id: Optional[str] = None,
        category_id: Optional[str] = None,
    ) -> Tuple[List[Transaction], int]:
        with self._get_db() as db:
            q = db.query(TransactionModel).filter(
                TransactionModel.family_group_id == family_group_id
            )
            if account_id:
                q = q.filter(TransactionModel.account_id == account_id)
            if category_id:
                q = q.filter(TransactionModel.category_id == category_id)

            total = q.count()
            rows = (
                q.order_by(TransactionModel.date.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return [self._to_domain(r) for r in rows], total

    def get_by_period(
        self, year: int, month: int, family_group_id: Optional[str] = None
    ) -> List[Transaction]:
        with self._get_db() as db:
            q = db.query(TransactionModel).filter(
                extract("year", TransactionModel.date) == year,
                extract("month", TransactionModel.date) == month,
            )
            if family_group_id:
                q = q.filter(
                    TransactionModel.family_group_id == family_group_id
                )
            return [self._to_domain(r) for r in q.all()]

    def delete(
        self, transaction_id: str, family_group_id: Optional[str] = None
    ) -> bool:
        with self._get_db() as db:
            q = db.query(TransactionModel).filter(
                TransactionModel.id == transaction_id
            )
            if family_group_id:
                q = q.filter(
                    TransactionModel.family_group_id == family_group_id
                )
            deleted = q.delete()
            db.commit()
            return deleted > 0

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
            family_group_id=row.family_group_id,
            date=row.date,
        )