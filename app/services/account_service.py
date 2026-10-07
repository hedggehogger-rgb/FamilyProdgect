from decimal import Decimal
from typing import Optional
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
            raise ValueError(f"Счёт '{account.id}' уже существует")
        self._account_repo.save(account)

    def get_account(self, account_id: str) -> Account:
        acc = self._account_repo.find_by_id(account_id)
        if not acc:
            raise KeyError(f"Счёт '{account_id}' не найден")
        return acc

    def add_transaction(self, transaction: Transaction) -> None:
        """Применяет транзакцию и обновляет балансы счетов."""
        self._apply_balance_changes(transaction, rollback=False)
        self._tx_repo.save(transaction)

    def delete_transaction(self, transaction_id: str) -> None:
        """Удаляет транзакцию и аккуратно откатывает баланс счетов."""
        tx = self._tx_repo.get_by_id(transaction_id)
        if not tx:
            raise KeyError(f"Транзакция '{transaction_id}' не найдена")

        # Откатываем финансовые изменения
        self._apply_balance_changes(tx, rollback=True)
        self._tx_repo.delete(transaction_id)

    def transfer_funds(
        self,
        from_account_id: str,
        to_account_id: str,
        amount: Decimal,
        author,
        note: str = "Перевод между счетами",
    ) -> Transaction:
        """Удобный метод для перевода средств с карты на карту / снятия налички."""
        from_acc = self.get_account(from_account_id)

        tx = Transaction(
            id="",  # Сгенерируется в роутере или репозитории
            type=TransactionType.TRANSFER,
            category_id=None,
            amount=amount,
            currency=from_acc.currency,
            account_id=from_account_id,
            to_account_id=to_account_id,
            author=author,
            note=note,
        )
        self.add_transaction(tx)
        return tx

    def _apply_balance_changes(
        self, tx: Transaction, rollback: bool = False
    ) -> None:
        """
        Внутренний механизм применения/отката баланса.
        Если rollback=True, операция разворачивается в обратную сторону.
        """
        from_acc = self.get_account(tx.account_id)
        amount_in_from_cur = self._converter.convert(
            tx.amount, tx.currency, from_acc.currency
        )

        if tx.type == TransactionType.INCOME:
            if not rollback:
                from_acc.deposit(amount_in_from_cur)
            else:
                from_acc.withdraw(amount_in_from_cur)
            self._account_repo.save(from_acc)

        elif tx.type in (
            TransactionType.EXPENSE_PLANNED,
            TransactionType.EXPENSE_IMPULSE,
            TransactionType.INVESTMENT,
        ):
            if not rollback:
                from_acc.withdraw(amount_in_from_cur)
            else:
                from_acc.deposit(amount_in_from_cur)
            self._account_repo.save(from_acc)

        elif tx.type == TransactionType.TRANSFER:
            to_acc = self.get_account(tx.to_account_id)
            amount_in_to_cur = self._converter.convert(
                tx.amount, tx.currency, to_acc.currency
            )

            if not rollback:
                from_acc.withdraw(amount_in_from_cur)
                to_acc.deposit(amount_in_to_cur)
            else:
                # Откат перевода
                to_acc.withdraw(amount_in_to_cur)
                from_acc.deposit(amount_in_from_cur)

            self._account_repo.save(from_acc)
            self._account_repo.save(to_acc)