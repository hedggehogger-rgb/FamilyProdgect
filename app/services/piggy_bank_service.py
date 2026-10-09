from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app.domain.models import Author, Currency, Transaction, TransactionType
from app.infrastructure.database import PiggyBankModel, PiggyBankNoteModel, SessionLocal
from app.services.account_service import AccountService
from app.services.currency_service import CurrencyConverter


class PiggyBankService:
    def __init__(self, account_svc: AccountService, converter: CurrencyConverter):
        self._account_svc = account_svc
        self._converter = converter

    def create_piggy_bank(
        self, name: str, target_amount: Decimal, account_id: str, currency: Currency = Currency.RUB,
        deadline: Optional[datetime] = None, is_auto_replenish: bool = False,
        auto_replenish_amount: Decimal = Decimal("0.00"), auto_replenish_day: Optional[int] = None,
        family_group_id: str = "",
    ) -> PiggyBankModel:
        self._account_svc.get_account(account_id, family_group_id)
        db: Session = SessionLocal()
        try:
            pb = PiggyBankModel(
                id=f"pb-{uuid.uuid4().hex[:8]}", family_group_id=family_group_id, name=name,
                target_amount=target_amount, current_amount=Decimal("0.00"), currency=currency.value,
                deadline=deadline, account_id=account_id, is_auto_replenish=is_auto_replenish,
                auto_replenish_amount=auto_replenish_amount, auto_replenish_day=auto_replenish_day, is_completed=False,
            )
            db.add(pb)
            db.commit()
            db.refresh(pb)
            return pb
        finally:
            db.close()

    def deposit(
        self, piggy_bank_id: str, amount: Decimal, account_id: str, author: Author,
        deposit_currency: Optional[Currency] = None, note_text: Optional[str] = None,
        family_group_id: Optional[str] = None,
    ) -> PiggyBankModel:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(PiggyBankModel.id == piggy_bank_id)
            if family_group_id:
                query = query.filter(PiggyBankModel.family_group_id == family_group_id)
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            chosen_currency = deposit_currency or Currency(pb.currency)
            amount_in_pb_cur = self._converter.convert(
                amount, chosen_currency, Currency(pb.currency)
            )

            tx_note = note_text or f"Ушло в копилку '{pb.name}'"
            tx = Transaction(
                id=str(uuid.uuid4()),
                type=TransactionType.EXPENSE_PLANNED,
                category_id=None,
                amount=amount,
                currency=chosen_currency,
                account_id=account_id,
                author=author,
                family_group_id=pb.family_group_id,
                date=datetime.utcnow(),
                note=tx_note,
            )
            self._account_svc.add_transaction(tx)

            pb.current_amount = Decimal(str(pb.current_amount)) + amount_in_pb_cur
            if pb.current_amount >= Decimal(str(pb.target_amount)):
                pb.is_completed = True
                pb.is_auto_replenish = False
                pb.snoozed_until = None
                pb.skip_until_month = None

            db.commit()
            db.refresh(pb)
            return pb
        finally:
            db.close()

    def toggle_auto_replenish(
        self, piggy_bank_id: str, is_auto_replenish: bool,
        amount: Optional[Decimal] = None, day: Optional[int] = None,
        account_id: Optional[str] = None, family_group_id: Optional[str] = None,
    ) -> PiggyBankModel:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(PiggyBankModel.id == piggy_bank_id)
            if family_group_id:
                query = query.filter(PiggyBankModel.family_group_id == family_group_id)
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            pb.is_auto_replenish = is_auto_replenish

            if not is_auto_replenish:
                # Отсрочка и пропуск сбрасываются при отключении автопополнения
                pb.snoozed_until = None
                pb.skip_until_month = None
            else:
                if amount is not None and amount > Decimal("0.00"):
                    pb.auto_replenish_amount = amount
                elif pb.auto_replenish_amount is None or Decimal(str(pb.auto_replenish_amount)) <= Decimal("0.00"):
                    pb.auto_replenish_amount = Decimal("1000.00")

                if day is not None and 1 <= day <= 31:
                    pb.auto_replenish_day = day
                elif pb.auto_replenish_day is None:
                    pb.auto_replenish_day = 1

                if account_id:
                    pb.account_id = account_id

            db.commit()
            db.refresh(pb)
            return pb
        finally:
            db.close()

    def snooze_auto_replenish(
        self, piggy_bank_id: str, snooze_date: Optional[datetime] = None,
        skip_current_month: bool = False, family_group_id: Optional[str] = None,
    ) -> PiggyBankModel:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(PiggyBankModel.id == piggy_bank_id)
            if family_group_id:
                query = query.filter(PiggyBankModel.family_group_id == family_group_id)
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            now = datetime.utcnow()
            if skip_current_month:
                pb.skip_until_month = f"{now.year:04d}-{now.month:02d}"
                pb.snoozed_until = None
            elif snooze_date:
                pb.snoozed_until = snooze_date
                pb.skip_until_month = None

            db.commit()
            db.refresh(pb)
            return pb
        finally:
            db.close()

    def add_note(self, piggy_bank_id: str, author: Author, text: str, family_group_id: Optional[str] = None) -> PiggyBankNoteModel:
        db: Session = SessionLocal()
        try:
            note = PiggyBankNoteModel(
                id=f"pbn-{uuid.uuid4().hex[:8]}",
                piggy_bank_id=piggy_bank_id,
                author=author.value,
                text=text,
                created_at=datetime.utcnow()
            )
            db.add(note)
            db.commit()
            db.refresh(note)
            return note
        finally:
            db.close()

    def get_all(self, family_group_id: Optional[str] = None) -> List[PiggyBankModel]:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel)
            if family_group_id:
                query = query.filter(PiggyBankModel.family_group_id == family_group_id)
            return query.all()
        finally:
            db.close()

    def get_notes(self, piggy_bank_id: str, family_group_id: Optional[str] = None) -> List[PiggyBankNoteModel]:
        db: Session = SessionLocal()
        try:
            return db.query(PiggyBankNoteModel).filter(PiggyBankNoteModel.piggy_bank_id == piggy_bank_id).order_by(PiggyBankNoteModel.created_at.desc()).all()
        finally:
            db.close()

    def delete_piggy_bank(
        self, piggy_bank_id: str, target_account_id: Optional[str] = None,
        author: Author = Author.HUSBAND, family_group_id: Optional[str] = None,
    ) -> dict:
        db: Session = SessionLocal()
        try:
            query = db.query(PiggyBankModel).filter(PiggyBankModel.id == piggy_bank_id)
            if family_group_id:
                query = query.filter(PiggyBankModel.family_group_id == family_group_id)
            pb = query.first()
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            current_funds = Decimal(str(pb.current_amount))

            if target_account_id and current_funds > 0:
                tx = Transaction(
                    id=str(uuid.uuid4()),
                    type=TransactionType.INCOME_UNPLANNED,
                    category_id=None,
                    amount=current_funds,
                    currency=Currency(pb.currency),
                    account_id=target_account_id,
                    author=author,
                    family_group_id=pb.family_group_id,
                    date=datetime.utcnow(),
                    note=f"Разбита копилка '{pb.name}'",
                )
                self._account_svc.add_transaction(tx)

            db.delete(pb)
            db.commit()
            return {"status": "success", "message": f"Копилка '{pb.name}' успешно удалена"}
        finally:
            db.close()