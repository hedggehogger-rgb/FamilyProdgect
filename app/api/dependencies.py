from app.domain.models import (
    Category,
    CategoryGroup,
    CategoryPeriodicity,
    RecurrenceFrequency,
)
from app.infrastructure.exchange_rate import ApiExchangeRateProvider
from app.infrastructure.repositories import (
    InMemoryAccountRepository,
    InMemoryCategoryRepository,
    PostgresTransactionRepository,  # <-- Подключили репозиторий PostgreSQL
)
from app.services.account_service import AccountService
from app.services.analytics_service import AnalyticsService
from app.services.budget_service import BudgetService
from app.services.currency_service import CurrencyConverter

# 1. Провайдеры и конвертер валют
rate_provider = ApiExchangeRateProvider()
currency_converter = CurrencyConverter(rate_provider)

# 2. Репозитории данных
account_repository = InMemoryAccountRepository()
category_repository = InMemoryCategoryRepository()
# Теперь транзакции сохраняются прямо в PostgreSQL внутри Docker:
transaction_repository = PostgresTransactionRepository()

# 3. Предзаполнение базовыми категориями по умолчанию
category_repository.add(
    Category(
        id="cat-salary",
        name="Зарплата",
        group=CategoryGroup.INCOME,
        periodicity=CategoryPeriodicity.INFINITE,
        frequency=RecurrenceFrequency.MONTHLY,
    )
)
category_repository.add(
    Category(
        id="cat-grocery",
        name="Продукты",
        group=CategoryGroup.EXPENSE,
        periodicity=CategoryPeriodicity.INFINITE,
    )
)

# 4. Доменные сервисы
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

budget_service = BudgetService(tx_repo=transaction_repository)


# 5. Функции внедрения зависимостей (Dependency Injection для FastAPI)
def get_account_service() -> AccountService:
    return account_service


def get_analytics_service() -> AnalyticsService:
    return analytics_service


def get_budget_service() -> BudgetService:
    return budget_service


def get_category_repository() -> InMemoryCategoryRepository:
    return category_repository


def get_currency_converter() -> CurrencyConverter:
    return currency_converter