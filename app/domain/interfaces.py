from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional
from app.domain.models import Account, Category, Currency, Transaction


class IExchangeRateProvider(ABC):

    @abstractmethod
    def get_rates_to_usd(self) -> Dict[Currency, Decimal]:
        pass


class IAccountRepository(ABC):

    @abstractmethod
    def save(self, account: Account) -> None:
        pass

    @abstractmethod
    def find_by_id(self, account_id: str) -> Optional[Account]:
        pass

    @abstractmethod
    def find_all(self) -> List[Account]:
        pass


class ICategoryRepository(ABC):

    @abstractmethod
    def add(self, category: Category) -> None:
        pass

    @abstractmethod
    def get_by_id(self, category_id: str) -> Optional[Category]:
        pass

    @abstractmethod
    def get_all(self) -> List[Category]:
        pass


class ITransactionRepository(ABC):

    @abstractmethod
    def save(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Transaction]:
        pass

    @abstractmethod
    def get_by_period(self, year: int, month: int) -> List[Transaction]:
        pass