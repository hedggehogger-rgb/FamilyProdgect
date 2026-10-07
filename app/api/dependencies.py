from app.infrastructure.exchange_rate import ApiExchangeRateProvider
from app.infrastructure.repositories import (
    PostgresAccountRepository,  # <-- Счета в PostgreSQL
    PostgresCategoryRepository,
    PostgresTransactionRepository,
)

from app.services.account_service import AccountService
from app.services.analytics_service import AnalyticsService
from app.services.budget_service import BudgetService
from app.services.currency_service import CurrencyConverter

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.infrastructure.database import SessionLocal, UserModel
from app.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный или просроченный токен авторизации",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = AuthService.decode_token(token)
    if not payload:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    db: Session = SessionLocal()
    try:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise credentials_exception
        return user
    finally:
        db.close()


# 1. Провайдеры и конвертер
rate_provider = ApiExchangeRateProvider()
currency_converter = CurrencyConverter(rate_provider)

# 2. Все три репозитория теперь хранят данные в базе в Docker
account_repository = PostgresAccountRepository()
category_repository = PostgresCategoryRepository()
transaction_repository = PostgresTransactionRepository()

# 3. Сервисы
account_service = AccountService(
    account_repo=account_repository,
    tx_repo=transaction_repository,
    converter=currency_converter,
)

analytics_service = AnalyticsService(
    tx_repo=transaction_repository,
    cat_repo=category_repository,
    converter=currency_converter,
)

budget_service = BudgetService(
    tx_repo=transaction_repository,
    cat_repo=category_repository,
    converter=currency_converter,
)


def get_account_service() -> AccountService:
    return account_service


def get_analytics_service() -> AnalyticsService:
    return analytics_service


def get_budget_service() -> BudgetService:
    return budget_service


def get_category_repository() -> PostgresCategoryRepository:
    return category_repository


def get_currency_converter() -> CurrencyConverter:
    return currency_converter