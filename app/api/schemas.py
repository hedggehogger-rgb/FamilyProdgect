from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.models import (
    Author,
    CategoryGroup,
    CategoryPeriodicity,
    Currency,
    RecurrenceFrequency,
    TransactionType,
)


class AccountCreateSchema(BaseModel):
    id: str
    name: str
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
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity
    months_duration: int = 0
    frequency: RecurrenceFrequency = RecurrenceFrequency.NONE
    day_of_month: Optional[int] = None


class TransactionCreateSchema(BaseModel):
    id: Optional[str] = None
    type: TransactionType
    category_id: str
    amount: Decimal = Field(gt=0)
    currency: Currency
    account_id: str
    author: Author
    note: str = ""
    date: Optional[datetime] = None


class MonthlyReportResponseSchema(BaseModel):
    year: int
    month: int
    currency: Currency
    total_income: Decimal
    total_expense: Decimal
    net_savings: Decimal