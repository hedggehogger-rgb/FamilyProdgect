from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
from app.domain.interfaces import ICategoryRepository, ITransactionRepository
from app.domain.models import CategoryGroup, Currency
from app.services.currency_service import CurrencyConverter


@dataclass
class MonthlyReport:
    year: int
    month: int
    currency: Currency
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal


class AnalyticsService:

    def __init__(
        self,
        tx_repo: ITransactionRepository,
        cat_repo: ICategoryRepository,
        converter: CurrencyConverter,
    ):
        self._tx_repo = tx_repo
        self._cat_repo = cat_repo
        self._converter = converter

    def get_monthly_report(
        self,
        year: int,
        month: int,
        target_currency: Currency,
        family_group_id: Optional[str] = None,
    ) -> MonthlyReport:
        txs = self._tx_repo.get_by_period(year, month, family_group_id)
        income = Decimal("0.00")
        expense = Decimal("0.00")

        for tx in txs:
            cat = (
                self._cat_repo.get_by_id(tx.category_id, family_group_id)
                if tx.category_id
                else None
            )
            val = self._converter.convert(
                tx.amount, tx.currency, target_currency
            )
            if cat and cat.group == CategoryGroup.INCOME:
                income += val
            elif cat and cat.group == CategoryGroup.EXPENSE:
                expense += val

        return MonthlyReport(
            year=year,
            month=month,
            currency=target_currency,
            total_income=income,
            total_expense=expense,
            net_savings=income - expense,
        )

    def get_expenses_by_recurrence(
        self,
        year: int,
        month: int,
        target_currency: Currency,
        family_group_id: Optional[str] = None,
    ) -> Dict[str, Decimal]:
        txs = self._tx_repo.get_by_period(year, month, family_group_id)
        result = defaultdict(lambda: Decimal("0.00"))

        for tx in txs:
            cat = (
                self._cat_repo.get_by_id(tx.category_id, family_group_id)
                if tx.category_id
                else None
            )
            if cat and cat.group == CategoryGroup.EXPENSE:
                freq = cat.frequency.value
                val = self._converter.convert(
                    tx.amount, tx.currency, target_currency
                )
                result[freq] += val
        return dict(result)