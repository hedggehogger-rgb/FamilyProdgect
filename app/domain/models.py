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

    @property
    def ru_label(self) -> str:
        return "Любими Муж" if self == Author.HUSBAND else "КошкоЖена"


class CategoryGroup(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    INVESTMENT = "INVESTMENT"


class CategoryPeriodicity(str, Enum):
    INFINITE = "INFINITE"
    LIMITED = "LIMITED"


class RecurrenceFrequency(str, Enum):
    NONE = "NONE"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUALLY = "ANNUALLY"


class TransactionType(str, Enum):
    INCOME = "INCOME"
    INCOME_PLANNED = "INCOME_PLANNED"
    INCOME_UNPLANNED = "INCOME_UNPLANNED"
    EXPENSE_PLANNED = "EXPENSE_PLANNED"
    EXPENSE_IMPULSE = "EXPENSE_IMPULSE"
    INVESTMENT = "INVESTMENT"
    TRANSFER = "TRANSFER"


@dataclass
class Transaction:
    id: str
    type: TransactionType
    category_id: Optional[str]
    amount: Decimal
    currency: Currency
    account_id: str
    author: Author
    note: str = ""
    to_account_id: Optional[str] = None
    family_group_id: Optional[str] = None
    date: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.amount <= Decimal("0"):
            raise ValueError("Сумма транзакции должна быть строго больше 0")
        if self.type == TransactionType.TRANSFER and not self.to_account_id:
            raise ValueError("Для перевода необходимо указать целевой счёт")
        if self.type == TransactionType.TRANSFER and self.account_id == self.to_account_id:
            raise ValueError("Нельзя перевести деньги на тот же самый счёт")


@dataclass
class Category:
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity = CategoryPeriodicity.INFINITE
    months_duration: int = 0
    frequency: RecurrenceFrequency = RecurrenceFrequency.NONE
    day_of_month: Optional[int] = None
    day_of_week: Optional[int] = None
    recurrence_month: Optional[int] = None
    color: str = "#8b5cf6"
    family_group_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_active_at(self, year: int, month: int) -> bool:
        if self.periodicity == CategoryPeriodicity.INFINITE:
            return True
        start_year = self.created_at.year
        start_month = self.created_at.month
        months_passed = (year - start_year) * 12 + (month - start_month)
        return 0 <= months_passed < self.months_duration


@dataclass
class Account:
    id: str
    name: str
    currency: Currency = Currency.RUB
    balance: Decimal = Decimal("0.00")
    is_investment: bool = False
    family_group_id: Optional[str] = None

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
            raise ValueError(f"Недостаточно средств на счете {self.name}")
        self.balance -= amount