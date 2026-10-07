from app.domain.interfaces import IAccountRepository, ITransactionRepository
from app.domain.models import Account, Transaction, TransactionType
from app.services.currency_service import CurrencyConverter


class AccountService:

    def __init__(
        self,
        account_repo: IAccountRepository,
        tx_repo: ITransactionRepository,
        converter: CurrencyConverter,
    ):
        self._account_repo = account_repo
        self._tx_repo = tx_repo
        self._converter = converter

    def create_account(self, account: Account) -> None:
        if self._account_repo.find_by_id(account.id):
            raise ValueError(f"Счёт {account.id} уже существует")
        self._account_repo.save(account)

    def get_account(self, account_id: str) -> Account:
        acc = self._account_repo.find_by_id(account_id)
        if not acc:
            raise KeyError(f"Счёт {account_id} не найден")
        return acc

    def add_transaction(self, transaction: Transaction) -> None:
        account = self.get_account(transaction.account_id)
        amount_in_acc = self._converter.convert(
            amount=transaction.amount,
            from_cur=transaction.currency,
            to_cur=account.currency,
        )

        if transaction.type == TransactionType.INCOME:
            account.deposit(amount_in_acc)
        else:
            account.withdraw(amount_in_acc)

        self._account_repo.save(account)
        self._tx_repo.save(transaction)