from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from app.domain.interfaces import ITransactionRepository


class BudgetService:
    def __init__(self, tx_repo: ITransactionRepository):
        self._tx_repo = tx_repo

    def get_average_expense_for_category(self, category_id: str, months_back: int = 3) -> Decimal:
        now = datetime.now()
        total = Decimal("0.00")
        count = 0

        current_year = now.year
        current_month = now.month

        for i in range(1, months_back + 1):
            target_month = current_month - i
            target_year = current_year

            while target_month <= 0:
                target_month += 12
                target_year -= 1

            txs = self._tx_repo.get_by_period(target_year, target_month)
            cat_expenses = sum(
                (tx.amount for tx in txs if tx.category_id == category_id),
                Decimal("0.00")
            )
            total += cat_expenses
            count += 1

        if count > 0:
            return (total / Decimal(count)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal("0.00")