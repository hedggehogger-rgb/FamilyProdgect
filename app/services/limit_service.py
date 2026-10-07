from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
import uuid
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
    status_marker: str  # OK, WARNING, OVERSPENT


class LimitService:

    def __init__(self, converter: CurrencyConverter):
        self._converter = converter

    def set_limit(
        self,
        category_id: str,
        limit_amount: Decimal,
        currency: Currency = Currency.RUB,
        months_duration: int = 1,
    ) -> CategoryLimitModel:
        db: Session = SessionLocal()
        try:
            limit = CategoryLimitModel(
                id=f"lim-{uuid.uuid4().hex[:8]}",
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

    def get_category_limit_status(
        self,
        category_id: str,
        target_year: int,
        target_month: int,
    ) -> Optional[LimitStatus]:
        db: Session = SessionLocal()
        try:
            # Ищем актуальный лимит для категории
            limit = (
                db.query(CategoryLimitModel)
                .filter(CategoryLimitModel.category_id == category_id)
                .order_by(CategoryLimitModel.created_at.desc())
                .first()
            )
            if not limit:
                return None

            cat = (
                db.query(CategoryModel)
                .filter(CategoryModel.id == category_id)
                .first()
            )
            cat_name = cat.name if cat else "Категория"

            # Считаем сумму расходов за указанный месяц
            limit_curr = Currency(limit.currency)
            txs = (
                db.query(TransactionModel)
                .filter(
                    TransactionModel.category_id == category_id,
                    TransactionModel.type.in_(
                        ["EXPENSE_PLANNED", "EXPENSE_IMPULSE"]
                    ),
                )
                .all()
            )

            spent = Decimal("0.00")
            for tx in txs:
                if tx.date.year == target_year and tx.date.month == target_month:
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
            if is_exceeded:
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
                is_active=True,
                status_marker=marker,
            )
        finally:
            db.close()