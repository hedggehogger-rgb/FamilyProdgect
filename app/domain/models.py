from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class Currency(str, Enum):
    RUB = "RUB"
    AMD = "AMD"
    USD = "USD"

    @property
    def symbol(self) -> str:
        symbols = {self.RUB: "₽", self.AMD: "֏", self.USD: "$"}
        return symbols.get(self, "")


class Author(str, Enum):
    HUSBAND = "HUSBAND"
    WIFE = "WIFE"


class CategoryGroup(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    INVESTMENT = "INVESTMENT"


class CategoryPeriodicity(str, Enum):
    INFINITE = "INFINITE"
    LIMITED = "LIMITED"


class RecurrenceFrequency(str, Enum):
    NONE = "NONE"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE_PLANNED = "EXPENSE_PLANNED"
    EXPENSE_IMPULSE = "EXPENSE_IMPULSE"
    INVESTMENT = "INVESTMENT"


@dataclass
class Category:
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity
    months_duration: int = 0
    frequency: RecurrenceFrequency = RecurrenceFrequency.NONE
    day_of_month: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.frequency != RecurrenceFrequency.NONE:
            cycles = {
                RecurrenceFrequency.WEEKLY: 8,
                RecurrenceFrequency.MONTHLY: 2,
            }.get(self.frequency, 1)

            if (
                self.periodicity == CategoryPeriodicity.LIMITED
                and self.months_duration < cycles
            ):
                raise ValueError(
                    "Срок действия должен покрывать минимум 2 цикла повторений"
                )


@dataclass
class Account:
    id: str
    name: str
    currency: Currency = Currency.RUB
    balance: Decimal = Decimal("0.00")
    is_investment: bool = False

    def can_withdraw(self, amount: Decimal) -> bool:
        return self.balance >= amount

    def deposit(self, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError("Сумма пополнения должна быть больше 0")
        self.balance += amount

    def withdraw(self, amount: Decimal) -> None:
        if amount <= Decimal("0"):
            raise ValueError("Сумма списания должна быть больше 0")
        if not self.can_withdraw(amount):
            raise ValueError(
                f"Недостаточно средств на счете {self.name} (Баланс: {self.balance} {self.currency.symbol})"
            )
        self.balance -= amount


@dataclass
class Transaction:
    id: str
    type: TransactionType
    category_id: str
    amount: Decimal
    currency: Currency
    account_id: str
    author: Author
    note: str
    date: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.amount <= Decimal("0"):
            raise ValueError("Сумма транзакции должна быть строго больше 0")