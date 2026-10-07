from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app.domain.models import Author, Currency
from app.infrastructure.database import (
    PiggyBankModel,
    PiggyBankNoteModel,
    SessionLocal,
)
from app.services.account_service import AccountService
from app.services.currency_service import CurrencyConverter


class PiggyBankService:

    def __init__(
        self, account_svc: AccountService, converter: CurrencyConverter
    ):
        self._account_svc = account_svc
        self._converter = converter

    def create_piggy_bank(
        self,
        name: str,
        target_amount: Decimal,
        account_id: str,
        currency: Currency = Currency.RUB,
        deadline: Optional[datetime] = None,
        is_auto_replenish: bool = False,
        auto_replenish_amount: Decimal = Decimal("0.00"),
        auto_replenish_day: Optional[int] = None,
        family_group_id: str = "",
    ) -> PiggyBankModel:
        # Проверяем, что счёт существует и принадлежит семье
        self._account_svc.get_account(account_id, family_group_id)

        db: Session = SessionLocal()
        try:
            pb = PiggyBankModel(
                id=f"pb-{uuid.uuid4().hex[:8]}",
                family_group_id=family_group_id,
                name=name,
                target_amount=target_amount,
                current_amount=Decimal("0.00"),
                currency=currency.value,
                deadline=deadline,
                account_id=account_id,
                is_auto_replenish=is_auto_replenish,
                auto_replenish_amount=auto_replenish_amount,
                auto_replenish_day=auto_replenish_day,
                is_completed=False,
            )
            db.add(pb)
            db.commit()
            db.refresh(pb)
            return pb
        finally:
            db.close()

    def deposit(
        self,
        piggy_bank_id: str,
        amount: Decimal,
        author: Author,
        note_text: Optional[str] = None,
        family_group_id: Optional[str] = None,
    ) -> PiggyBankModel:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(
                PiggyBankModel.id == piggy_bank_id
            )
            if family_group_id:
                query = query.filter(
                    PiggyBankModel.family_group_id == family_group_id
                )
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            account = self._account_svc.get_account(
                pb.account_id, pb.family_group_id
            )
            amount_in_acc_cur = self._converter.convert(
                amount, Currency(pb.currency), account.currency
            )
            account.withdraw(amount_in_acc_cur)
            self._account_svc._account_repo.save(account)

            pb.current_amount = Decimal(str(pb.current_amount)) + amount

            if pb.current_amount >= Decimal(str(pb.target_amount)):
                pb.is_completed = True
                pb.is_auto_replenish = False

            if note_text:
                note = PiggyBankNoteModel(
                    id=f"note-{uuid.uuid4().hex[:8]}",
                    piggy_bank_id=pb.id,
                    author=author.value,
                    text=note_text,
                )
                db.add(note)

            db.commit()
            db.refresh(pb)
            return pb
        finally:
            db.close()

    def add_note(
        self,
        piggy_bank_id: str,
        author: Author,
        text: str,
        family_group_id: Optional[str] = None,
    ) -> PiggyBankNoteModel:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(
                PiggyBankModel.id == piggy_bank_id
            )
            if family_group_id:
                query = query.filter(
                    PiggyBankModel.family_group_id == family_group_id
                )
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            note = PiggyBankNoteModel(
                id=f"note-{uuid.uuid4().hex[:8]}",
                piggy_bank_id=pb.id,
                author=author.value,
                text=text,
            )
            db.add(note)
            db.commit()
            db.refresh(note)
            return note
        finally:
            db.close()

    def get_all(
        self, family_group_id: Optional[str] = None
    ) -> List[PiggyBankModel]:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel)
            if family_group_id:
                query = query.filter(
                    PiggyBankModel.family_group_id == family_group_id
                )
            return query.all()
        finally:
            db.close()

    def get_notes(
        self, piggy_bank_id: str, family_group_id: Optional[str] = None
    ) -> List[PiggyBankNoteModel]:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(
                PiggyBankModel.id == piggy_bank_id
            )
            if family_group_id:
                query = query.filter(
                    PiggyBankModel.family_group_id == family_group_id
                )
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            return (
                db.query(PiggyBankNoteModel)
                .filter(PiggyBankNoteModel.piggy_bank_id == pb.id)
                .order_by(PiggyBankNoteModel.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def delete_piggy_bank(
        self,
        piggy_bank_id: str,
        return_funds_to_account: bool = True,
        family_group_id: Optional[str] = None,
    ) -> dict:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(
                PiggyBankModel.id == piggy_bank_id
            )
            if family_group_id:
                query = query.filter(
                    PiggyBankModel.family_group_id == family_group_id
                )
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            current_funds = Decimal(str(pb.current_amount))

            if return_funds_to_account and current_funds > 0:
                account = self._account_svc.get_account(
                    pb.account_id, pb.family_group_id
                )
                amount_in_acc = self._converter.convert(
                    current_funds, Currency(pb.currency), account.currency
                )
                account.deposit(amount_in_acc)
                self._account_svc._account_repo.save(account)

            db.delete(pb)
            db.commit()
            return {
                "status": "success",
                "message": f"Копилка удалена. {current_funds} {pb.currency} возвращено на счёт {pb.account_id}",
            }
        finally:
            db.close()