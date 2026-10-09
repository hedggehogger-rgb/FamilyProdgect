from decimal import Decimal
from typing import List, Optional
from app.domain.interfaces import IAccountRepository
from app.domain.models import Account, Currency
from app.infrastructure.database import AccountModel
from app.infrastructure.repositories.base import BasePostgresRepository


class PostgresAccountRepository(BasePostgresRepository, IAccountRepository):

    def save(self, account: Account) -> None:
        with self._get_db() as db:
            model = AccountModel(
                id=account.id,
                family_group_id=account.family_group_id,
                name=account.name,
                currency=account.currency.value,
                balance=account.balance,
                is_investment=account.is_investment,
            )
            db.merge(model)
            db.commit()

    def find_by_id(
        self, account_id: str, family_group_id: Optional[str] = None
    ) -> Optional[Account]:
        with self._get_db() as db:
            q = db.query(AccountModel).filter(AccountModel.id == account_id)
            if family_group_id:
                q = q.filter(AccountModel.family_group_id == family_group_id)
            row = q.first()
            return self._to_domain(row) if row else None

    def find_all(self, family_group_id: Optional[str] = None) -> List[Account]:
        with self._get_db() as db:
            q = db.query(AccountModel)
            if family_group_id:
                q = q.filter(AccountModel.family_group_id == family_group_id)
            return [self._to_domain(r) for r in q.all()]

    def delete(
        self, account_id: str, family_group_id: Optional[str] = None
    ) -> bool:
        with self._get_db() as db:
            q = db.query(AccountModel).filter(AccountModel.id == account_id)
            if family_group_id:
                q = q.filter(AccountModel.family_group_id == family_group_id)
            deleted = q.delete()
            db.commit()
            return deleted > 0

    @staticmethod
    def _to_domain(row: AccountModel) -> Account:
        return Account(
            id=row.id,
            name=row.name,
            currency=Currency(row.currency),
            balance=Decimal(str(row.balance)),
            is_investment=row.is_investment,
            family_group_id=row.family_group_id,
        )