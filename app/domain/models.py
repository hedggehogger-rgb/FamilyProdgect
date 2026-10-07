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
    INFINITE = "INFINITE"  # Бессрочно
    LIMITED = "LIMITED"  # На сколько-то месяцев


class RecurrenceFrequency(str, Enum):
    NONE = "NONE"  # Нерегулярный
    WEEKLY = "WEEKLY"  # Раз в неделю
    MONTHLY = "MONTHLY"  # Раз в месяц
    QUARTERLY = "QUARTERLY"  # Раз в квартал (3 мес)
    ANNUALLY = "ANNUALLY"  # Раз в год (12 мес)


class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE_PLANNED = "EXPENSE_PLANNED"
    EXPENSE_IMPULSE = "EXPENSE_IMPULSE"
    INVESTMENT = "INVESTMENT"
    TRANSFER = "TRANSFER"  # <-- Перевод между счетами


@dataclass
class Transaction:
    id: str
    type: TransactionType
    category_id: Optional[str]  # Для перевода категория не обязательна
    amount: Decimal
    currency: Currency
    account_id: str
    author: Author
    note: str
    to_account_id: Optional[str] = (
        None  # Целевой счет при типе TRANSFER
    )
    date: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.amount <= Decimal("0"):
            raise ValueError("Сумма транзакции должна быть строго больше 0")
        if self.type == TransactionType.TRANSFER and not self.to_account_id:
            raise ValueError(
                "Для перевода необходимо указать целевой счёт (to_account_id)"
            )
        if self.type == TransactionType.TRANSFER and self.account_id == self.to_account_id:
            raise ValueError("Нельзя перевести деньги на тот же самый счёт")

@dataclass
class Category:
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity
    months_duration: int = 0
    frequency: RecurrenceFrequency = RecurrenceFrequency.NONE
    day_of_month: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        # 1. Валидация дня месяца для регулярных ежемесячных категорий
        if (
            self.frequency == RecurrenceFrequency.MONTHLY
            and self.day_of_month is not None
        ):
            if not (1 <= self.day_of_month <= 31):
                raise ValueError("День месяца должен быть в диапазоне от 1 до 31")

        # 2. Правило минимум 2 циклов повторений для ограниченных категорий
        if (
            self.periodicity == CategoryPeriodicity.LIMITED
            and self.frequency != RecurrenceFrequency.NONE
        ):
            # Минимально необходимое число месяцев для покрытия 2 циклов:
            min_months_required = {
                RecurrenceFrequency.WEEKLY: 1,  # 2 недели укладываются в 1 месяц
                RecurrenceFrequency.MONTHLY: 2,  # 2 месяца
                RecurrenceFrequency.QUARTERLY: 6,  # 2 квартала = 6 месяцев
                RecurrenceFrequency.ANNUALLY: 24,  # 2 года = 24 месяца
            }.get(self.frequency, 0)

            if self.months_duration < min_months_required:
                raise ValueError(
                    f"Срок действия категории с частотой '{self.frequency.value}' "
                    f"должен покрывать минимум 2 цикла (требуется от {min_months_required} мес., указано: {self.months_duration})"
                )

    def is_active_at(self, year: int, month: int) -> bool:
        """Проверяет, действует ли категория в указанный месяц и год."""
        if self.periodicity == CategoryPeriodicity.INFINITE:
            return True

        # Считаем разницу в месяцах с момента создания
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
    date: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.amount <= Decimal("0"):
            raise ValueError("Сумма транзакции должна быть строго больше 0")