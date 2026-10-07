from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional
from app.domain.interfaces import ICategoryRepository, ITransactionRepository
from app.domain.models import Category, CategoryPeriodicity, Currency
from app.services.currency_service import CurrencyConverter


@dataclass
class CategoryBudgetForecast:
    category_id: str
    category_name: str
    target_currency: Currency
    average_monthly_expense: Decimal
    predicted_next_month: Decimal
    months_analyzed: int
    is_active_next_month: bool
    explanation: str


class BudgetService:

    def __init__(
        self,
        tx_repo: ITransactionRepository,
        cat_repo: ICategoryRepository,
        converter: CurrencyConverter,
    ):
        self._tx_repo = tx_repo
        self._cat_repo = cat_repo
        self._converter = converter

    def predict_category_budget(
        self,
        category_id: str,
        target_currency: Currency = Currency.RUB,
        months_back: int = 3,
    ) -> CategoryBudgetForecast:
        category: Optional[Category] = self._cat_repo.get_by_id(category_id)
        if not category:
            raise KeyError(f"Категория с id '{category_id}' не найдена")

        now = datetime.utcnow()

        # 1. Вычисляем следующий месяц для проверки активности
        next_month = now.month + 1 if now.month < 12 else 1
        next_year = now.year if now.month < 12 else now.year + 1
        is_active_next = category.is_active_at(next_year, next_month)

        # 2. Если категория временная и её срок истекает, прогнозировать траты на будущее не нужно
        if not is_active_next:
            return CategoryBudgetForecast(
                category_id=category.id,
                category_name=category.name,
                target_currency=target_currency,
                average_monthly_expense=Decimal("0.00"),
                predicted_next_month=Decimal("0.00"),
                months_analyzed=0,
                is_active_next_month=False,
                explanation=f"Срок действия временной категории '{category.name}' истекает. В следующем месяце трат не ожидается.",
            )

        # 3. Собираем историю за предыдущие месяцы
        total_spent = Decimal("0.00")
        actual_active_months_count = 0

        current_year = now.year
        current_month = now.month

        for i in range(1, months_back + 1):
            target_m = current_month - i
            target_y = current_year
            while target_m <= 0:
                target_m += 12
                target_y -= 1

            # Учитываем месяц, только если категория уже существовала в тот момент!
            if category.is_active_at(target_y, target_m):
                txs = self._tx_repo.get_by_period(target_y, target_m)

                # Считаем траты по этой категории с конвертацией в нужную валюту
                month_cat_sum = Decimal("0.00")
                for tx in txs:
                    if tx.category_id == category_id:
                        converted = self._converter.convert(
                            tx.amount, tx.currency, target_currency
                        )
                        month_cat_sum += converted

                total_spent += month_cat_sum
                actual_active_months_count += 1

        # 4. Расчет среднего арифметического
        if actual_active_months_count > 0:
            avg = (total_spent / Decimal(actual_active_months_count)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            prediction = avg
            explanation = (
                f"На основе {actual_active_months_count} мес. активной истории "
                f"средний расход составил {avg} {target_currency.symbol}."
            )
        else:
            avg = Decimal("0.00")
            prediction = Decimal("0.00")
            explanation = (
                "Категория новая, данных за предыдущие месяцы еще нет."
            )

        return CategoryBudgetForecast(
            category_id=category.id,
            category_name=category.name,
            target_currency=target_currency,
            average_monthly_expense=avg,
            predicted_next_month=prediction,
            months_analyzed=actual_active_months_count,
            is_active_next_month=True,
            explanation=explanation,
        )