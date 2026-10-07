from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.domain.models import (
    Author,
    CategoryGroup,
    CategoryPeriodicity,
    Currency,
    RecurrenceFrequency,
    TransactionType,
)


class AccountCreateSchema(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=100)
    currency: Currency = Currency.RUB
    balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    is_investment: bool = False


class AccountResponseSchema(BaseModel):
    id: str
    name: str
    currency: Currency
    balance: Decimal
    is_investment: bool


class CategoryCreateSchema(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=100)
    group: CategoryGroup
    periodicity: CategoryPeriodicity = CategoryPeriodicity.INFINITE
    months_duration: int = 0
    frequency: RecurrenceFrequency = RecurrenceFrequency.NONE
    day_of_month: Optional[int] = None

    @model_validator(mode="after")
    def validate_category(self):
        if self.frequency == RecurrenceFrequency.NONE:
            self.day_of_month = None

        if (
            self.periodicity == CategoryPeriodicity.LIMITED
            and self.frequency != RecurrenceFrequency.NONE
        ):
            min_cycles = {
                RecurrenceFrequency.WEEKLY: 1,
                RecurrenceFrequency.MONTHLY: 2,
                RecurrenceFrequency.QUARTERLY: 6,
                RecurrenceFrequency.ANNUALLY: 24,
            }.get(self.frequency, 0)
            if self.months_duration < min_cycles:
                raise ValueError(
                    f"Срок ограниченной регулярной категории должен покрывать минимум 2 цикла ({min_cycles} мес.)"
                )

        if (
            self.periodicity == CategoryPeriodicity.LIMITED
            and self.months_duration <= 0
        ):
            raise ValueError(
                "Для ограниченной категории months_duration должен быть > 0"
            )

        return self


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)


class CategoryResponseSchema(BaseModel):
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity
    months_duration: int
    frequency: RecurrenceFrequency
    day_of_month: Optional[int]
    created_at: datetime


class TransactionCreateSchema(BaseModel):
    id: Optional[str] = None
    type: TransactionType
    category_id: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    currency: Currency
    account_id: str = Field(..., min_length=1)
    to_account_id: Optional[str] = None
    author: Author
    note: str = ""
    date: Optional[datetime] = None


class TransferCreateSchema(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: Decimal = Field(..., gt=0)
    currency: Currency
    author: Author
    note: str = "Перевод между счетами"


class TransactionResponseSchema(BaseModel):
    id: str
    type: TransactionType
    category_id: Optional[str]
    amount: Decimal
    currency: Currency
    account_id: str
    to_account_id: Optional[str]
    author: Author
    note: str
    date: datetime


class MonthlyReportResponseSchema(BaseModel):
    year: int
    month: int
    currency: Currency
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal


class BudgetForecastResponseSchema(BaseModel):
    category_id: str
    category_name: str
    target_currency: Currency
    average_monthly_expense: Decimal
    predicted_next_month: Decimal
    months_analyzed: int
    is_active_next_month: bool
    explanation: str