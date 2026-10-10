from datetime import datetime
from decimal import Decimal
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from app.domain.models import (
    DEFAULT_CATEGORY_COLOR,
    Author,
    CategoryGroup,
    CategoryPeriodicity,
    Currency,
    RecurrenceFrequency,
    TransactionType,
)

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int


class ActionStatusResponse(BaseModel):
    status: str = "success"
    message: str
    id: Optional[str] = None


class FamilyRegisterSchema(BaseModel):
    family_name: str = Field(..., min_length=2)
    first_user_name: str = Field(..., min_length=2)
    first_user_email: str = Field(...)
    first_user_password: str = Field(..., min_length=6)
    first_user_role: Author = Author.HUSBAND


class UserJoinFamilySchema(BaseModel):
    family_group_id: str
    name: str = Field(..., min_length=2)
    email: str
    password: str = Field(..., min_length=6)
    role: Author = Author.WIFE


class FamilyInfoResponseSchema(BaseModel):
    id: str
    name: str
    members_count: int


class ForgotPasswordRequestSchema(BaseModel):
    email: str


class ResetPasswordConfirmSchema(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)


class DeleteAccountSchema(BaseModel):
    password: str = Field(..., min_length=1)


class UserProfileUpdateSchema(BaseModel):
    name: str = Field(..., min_length=2)


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    role: Author
    family_group_id: str


class UserResponseSchema(BaseModel):
    id: str
    name: str
    email: str
    role: Author
    family_group_id: str


class AccountCreateSchema(BaseModel):
    id: Optional[str] = None
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
    day_of_week: Optional[int] = None
    recurrence_month: Optional[int] = None
    color: str = DEFAULT_CATEGORY_COLOR
    default_amount: Optional[Decimal] = None
    default_currency: Optional[Currency] = Currency.RUB
    default_account_id: Optional[str] = None
    expires_at: Optional[datetime] = None


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    frequency: Optional[RecurrenceFrequency] = None
    day_of_month: Optional[int] = None
    day_of_week: Optional[int] = None
    recurrence_month: Optional[int] = None
    color: Optional[str] = None
    default_amount: Optional[Decimal] = None
    default_currency: Optional[Currency] = Currency.RUB
    default_account_id: Optional[str] = None
    expires_at: Optional[datetime] = None


class CategoryResponseSchema(BaseModel):
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity
    months_duration: int
    frequency: RecurrenceFrequency
    day_of_month: Optional[int]
    day_of_week: Optional[int]
    recurrence_month: Optional[int]
    color: str
    default_amount: Optional[Decimal] = None
    default_currency: Optional[Currency] = Currency.RUB
    default_account_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime


class TransactionCreateSchema(BaseModel):
    id: Optional[str] = None
    type: TransactionType
    category_id: Optional[str] = None
    amount: Decimal = Field(..., gt=0)
    currency: Currency = Currency.RUB
    account_id: str = Field(..., min_length=1)
    to_account_id: Optional[str] = None
    author: Optional[Author] = None
    note: str = ""
    date: Optional[datetime] = None


class TransferCreateSchema(BaseModel):
    from_account_id: str = Field(..., min_length=1)
    to_account_id: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0)
    currency: Currency = Currency.RUB
    author: Optional[Author] = None
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
    is_executed: bool = True


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


class SetLimitSchema(BaseModel):
    category_id: str
    limit_amount: Decimal = Field(..., gt=0)
    currency: Currency = Currency.RUB
    months_duration: int = Field(default=1, ge=1)


class LimitStatusResponseSchema(BaseModel):
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
    status_marker: str


class PiggyBankCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    target_amount: Decimal = Field(..., gt=0)
    account_id: str
    currency: Currency = Currency.RUB
    deadline: Optional[datetime] = None
    is_auto_replenish: bool = False
    auto_replenish_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    auto_replenish_day: Optional[int] = Field(default=None, ge=1, le=31)


class PiggyBankDepositSchema(BaseModel):
    amount: Decimal = Field(..., gt=0)
    account_id: str = Field(..., min_length=1)
    currency: Optional[Currency] = None
    author: Optional[Author] = None
    note: Optional[str] = None


class PiggyBankSnoozeSchema(BaseModel):
    snooze_date: Optional[datetime] = None
    skip_current_month: bool = False


class PiggyBankAutoReplenishToggleSchema(BaseModel):
    is_auto_replenish: bool
    auto_replenish_amount: Optional[Decimal] = None
    auto_replenish_day: Optional[int] = None
    account_id: Optional[str] = None


class PiggyBankNoteCreateSchema(BaseModel):
    author: Optional[Author] = None
    text: str = Field(..., min_length=1)


class PiggyBankNoteResponseSchema(BaseModel):
    id: str
    author: Author
    text: str
    created_at: datetime


class PiggyBankResponseSchema(BaseModel):
    id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    currency: Currency
    account_id: str
    deadline: Optional[datetime]
    is_auto_replenish: bool
    auto_replenish_amount: Decimal
    auto_replenish_day: Optional[int]
    is_completed: bool
    snoozed_until: Optional[datetime] = None
    skip_until_month: Optional[str] = None
    created_at: datetime