from decimal import Decimal
from typing import List, Optional
import uuid
from app.domain.interfaces import IAccountRepository, ITransactionRepository
from app.domain.models import Account, Author, Currency, Transaction, TransactionType
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
        if self._account_repo.find_by_id(account.id, account.family_group_id):
            raise ValueError(f"Счёт '{account.id}' уже существует")
        self._account_repo.save(account)

    def get_account(
        self, account_id: str, family_group_id: Optional[str] = None
    ) -> Account:
        acc = self._account_repo.find_by_id(account_id, family_group_id)
        if not acc:
            raise KeyError(f"Счёт '{account_id}' не найден")
        return acc

    def get_all_accounts(
        self, family_group_id: Optional[str] = None
    ) -> List[Account]:
        return self._account_repo.find_all(family_group_id)

    def add_transaction(self, transaction: Transaction) -> None:
        if transaction.is_executed:
            self._apply_balance_changes(transaction, rollback=False)
        self._tx_repo.save(transaction)

    def delete_transaction(
        self,
        transaction_id: str,
        family_group_id: Optional[str] = None,
        target_account_id: Optional[str] = None,
    ) -> None:
        tx = self._tx_repo.get_by_id(transaction_id, family_group_id)
        if not tx:
            raise KeyError(f"Транзакция '{transaction_id}' не найдена")

        if tx.is_executed:
            original_acc = self._account_repo.find_by_id(tx.account_id, family_group_id)
            if original_acc:
                self._apply_balance_changes(tx, rollback=True)
            elif target_account_id:
                target_acc = self.get_account(target_account_id, family_group_id)
                effective_tx = Transaction(
                    id=tx.id,
                    type=tx.type,
                    category_id=tx.category_id,
                    amount=tx.amount,
                    currency=tx.currency,
                    account_id=target_acc.id,
                    to_account_id=tx.to_account_id,
                    author=tx.author,
                    note=tx.note,
                    family_group_id=family_group_id,
                    date=tx.date,
                    is_executed=True,
                )
                self._apply_balance_changes(effective_tx, rollback=True)

        self._tx_repo.delete(transaction_id, family_group_id)

    def execute_deferred_transaction(
        self, transaction_id: str, family_group_id: Optional[str] = None
    ) -> None:
        tx = self._tx_repo.get_by_id(transaction_id, family_group_id)
        if not tx:
            raise KeyError(f"Транзакция '{transaction_id}' не найдена")
        if tx.is_executed:
            return

        self._apply_balance_changes(tx, rollback=False)
        tx.is_executed = True
        self._tx_repo.save(tx)

    def delete_account(
        self, account_id: str, family_group_id: Optional[str] = None
    ) -> bool:
        acc = self.get_account(account_id, family_group_id)
        return self._account_repo.delete(acc.id, family_group_id)

    def transfer_funds(
        self,
        from_account_id: str,
        to_account_id: str,
        amount: Decimal,
        author: Author,
        currency: Optional[Currency] = None,
        family_group_id: Optional[str] = None,
        note: str = "Перевод между счетами",
    ) -> Transaction:
        from_acc = self.get_account(from_account_id, family_group_id)
        self.get_account(to_account_id, family_group_id)
        tx_currency = currency or from_acc.currency

        tx = Transaction(
            id=str(uuid.uuid4()),
            type=TransactionType.TRANSFER,
            category_id=None,
            amount=amount,
            currency=tx_currency,
            account_id=from_account_id,
            to_account_id=to_account_id,
            author=author,
            family_group_id=family_group_id,
            note=note,
            is_executed=True,
        )
        self.add_transaction(tx)
        return tx

    def _apply_balance_changes(
        self, tx: Transaction, rollback: bool = False
    ) -> None:
        try:
            from_acc = self.get_account(tx.account_id, tx.family_group_id)
        except KeyError:
            if rollback:
                return
            raise

        amount_in_from_cur = self._converter.convert(
            tx.amount, tx.currency, from_acc.currency
        )

        if tx.type in (
            TransactionType.INCOME,
            TransactionType.INCOME_PLANNED,
            TransactionType.INCOME_UNPLANNED,
        ):
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
            try:
                to_acc = self.get_account(tx.to_account_id, tx.family_group_id)
            except KeyError:
                if rollback:
                    return
                raise

            amount_in_to_cur = self._converter.convert(
                tx.amount, tx.currency, to_acc.currency
            )

            if not rollback:
                from_acc.withdraw(amount_in_from_cur)
                to_acc.deposit(amount_in_to_cur)
            else:
                to_acc.withdraw(amount_in_to_cur)
                from_acc.deposit(amount_in_from_cur)

            self._account_repo.save(from_acc)
            self._account_repo.save(to_acc)