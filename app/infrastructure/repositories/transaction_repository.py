from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy import extract
from app.domain.interfaces import ITransactionRepository
from app.domain.models import Author, Currency, Transaction, TransactionType
from app.infrastructure.database import TransactionModel
from app.infrastructure.repositories.base import BasePostgresRepository


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
                is_executed=transaction.is_executed,
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

    def get_deferred(self, family_group_id: str) -> List[Transaction]:
        with self._get_db() as db:
            q = (
                db.query(TransactionModel)
                .filter(
                    TransactionModel.family_group_id == family_group_id,
                    TransactionModel.is_executed == False,
                )
                .order_by(TransactionModel.date.asc())
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
            is_executed=getattr(row, "is_executed", True),
        )