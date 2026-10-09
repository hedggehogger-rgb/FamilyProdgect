from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import uuid
from sqlalchemy import extract
from sqlalchemy.orm import Session
from app.domain.models import Currency
from app.infrastructure.database import (
    CategoryLimitModel,
    CategoryModel,
    SessionLocal,
    TransactionModel,
)
from app.services.currency_service import CurrencyConverter


@dataclass
class LimitStatus:
    limit_id: str
    category_id: str
    category_name: str
    limit_amount: Decimal
    spent_amount: Decimal
    currency: Currency
    remaining_amount: Decimal
    is_exceeded: bool
    overspent_amount: Decimal
    percentage_used: Decimal
    is_active: bool
    status_marker: str


class LimitService:

    def __init__(self, converter: CurrencyConverter):
        self._converter = converter

    def set_limit(
        self,
        category_id: str,
        limit_amount: Decimal,
        currency: Currency = Currency.RUB,
        months_duration: int = 1,
        family_group_id: str = "",
    ) -> CategoryLimitModel:
        db: Session = SessionLocal()
        try:
            limit = CategoryLimitModel(
                id=f"lim-{uuid.uuid4().hex[:8]}",
                family_group_id=family_group_id,
                category_id=category_id,
                limit_amount=limit_amount,
                currency=currency.value,
                months_duration=months_duration,
                start_date=datetime.utcnow(),
            )
            db.add(limit)
            db.commit()
            db.refresh(limit)
            return limit
        finally:
            db.close()

    def delete_limit(self, category_id: str, family_group_id: str) -> bool:
        """Полное удаление лимитов для категории"""
        db: Session = SessionLocal()
        try:
            deleted = (
                db.query(CategoryLimitModel)
                .filter(
                    CategoryLimitModel.category_id == category_id,
                    CategoryLimitModel.family_group_id == family_group_id,
                )
                .delete()
            )
            db.commit()
            return deleted > 0
        finally:
            db.close()

    def get_category_limit_status(
        self,
        category_id: str,
        target_year: int,
        target_month: int,
        family_group_id: str,
    ) -> Optional[LimitStatus]:
        db: Session = SessionLocal()
        try:
            limit = (
                db.query(CategoryLimitModel)
                .filter(
                    CategoryLimitModel.category_id == category_id,
                    CategoryLimitModel.family_group_id == family_group_id,
                )
                .order_by(CategoryLimitModel.created_at.desc())
                .first()
            )
            if not limit:
                return None

            cat = (
                db.query(CategoryModel)
                .filter(
                    CategoryModel.id == category_id,
                    CategoryModel.family_group_id == family_group_id,
                )
                .first()
            )
            cat_name = cat.name if cat else "Категория"

            start_year = limit.start_date.year
            start_month = limit.start_date.month
            months_passed = (target_year - start_year) * 12 + (target_month - start_month)
            is_active = 0 <= months_passed < limit.months_duration

            limit_curr = Currency(limit.currency)
            txs = (
                db.query(TransactionModel)
                .filter(
                    TransactionModel.family_group_id == family_group_id,
                    TransactionModel.category_id == category_id,
                    TransactionModel.type.in_(["EXPENSE_PLANNED", "EXPENSE_IMPULSE"]),
                    TransactionModel.is_executed == True,
                    extract("year", TransactionModel.date) == target_year,
                    extract("month", TransactionModel.date) == target_month,
                )
                .all()
            )

            spent = Decimal("0.00")
            for tx in txs:
                converted = self._converter.convert(
                    Decimal(str(tx.amount)),
                    Currency(tx.currency),
                    limit_curr,
                )
                spent += converted

            limit_val = Decimal(str(limit.limit_amount))
            is_exceeded = spent > limit_val
            overspent = spent - limit_val if is_exceeded else Decimal("0.00")
            remaining = limit_val - spent if not is_exceeded else Decimal("0.00")
            pct = (
                (spent / limit_val * Decimal(100)).quantize(
                    Decimal("0.1"), rounding=ROUND_HALF_UP
                )
                if limit_val > 0
                else Decimal(0)
            )

            marker = "OK"
            if not is_active:
                marker = "EXPIRED"
            elif is_exceeded:
                marker = "OVERSPENT"
            elif pct >= Decimal("80.0"):
                marker = "WARNING"

            return LimitStatus(
                limit_id=limit.id,
                category_id=category_id,
                category_name=cat_name,
                limit_amount=limit_val,
                spent_amount=spent,
                currency=limit_curr,
                remaining_amount=remaining,
                is_exceeded=is_exceeded,
                overspent_amount=overspent,
                percentage_used=pct,
                is_active=is_active,
                status_marker=marker,
            )
        finally:
            db.close()