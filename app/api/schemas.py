from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.domain.models import (
    Author,
    CategoryGroup,
    CategoryPeriodicity,
    Currency,
    RecurrenceFrequency,
    TransactionType,
)


class AccountCreateSchema(BaseModel):
    id: str = Field(..., min_length=1, description="Уникальный ID счета")
    name: str = Field(
        ..., min_length=1, max_length=100, description="Название счета"
    )
    currency: Currency = Currency.RUB
    balance: Decimal = Field(default=Decimal("0.00"), ge=0)
    is_investment: bool = False


class AccountResponseSchema(BaseModel):
    id: str
    name: str
    currency: Currency
    balance: Decimal
    is_investment: bool


class CategoryResponseSchema(BaseModel):
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity
    frequency: RecurrenceFrequency


class TransactionCreateSchema(BaseModel):
    id: Optional[str] = None
    type: TransactionType
    category_id: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0, description="Сумма должна быть строго > 0")
    currency: Currency
    account_id: str = Field(..., min_length=1)
    author: Author
    note: str = ""
    date: Optional[datetime] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Сумма транзакции должна быть больше 0")
        return v


class MonthlyReportResponseSchema(BaseModel):
    year: int
    month: int
    currency: Currency
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal