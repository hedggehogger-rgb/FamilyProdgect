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
    ) -> PiggyBankModel:
        db: Session = SessionLocal()
        try:
            pb = PiggyBankModel(
                id=f"pb-{uuid.uuid4().hex[:8]}",
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
    ) -> PiggyBankModel:
        """Пополнение копилки: деньги списываются с привязанного счёта."""
        db: Session = SessionLocal()
        try:
            pb = (
                db.query(PiggyBankModel)
                .filter(PiggyBankModel.id == piggy_bank_id)
                .first()
            )
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            # 1. Списываем средства с основного счёта
            account = self._account_svc.get_account(pb.account_id)
            amount_in_acc_cur = self._converter.convert(
                amount, Currency(pb.currency), account.currency
            )
            account.withdraw(amount_in_acc_cur)
            self._account_svc._account_repo.save(account)

            # 2. Пополняем копилку
            pb.current_amount = Decimal(str(pb.current_amount)) + amount

            # 3. ПРОВЕРКА НАПОЛНЕНИЯ: если собрано, отключаем автопополнение!
            if pb.current_amount >= Decimal(str(pb.target_amount)):
                pb.is_completed = True
                pb.is_auto_replenish = (
                    False  # Автоматически останавливаем автоплатежи!
                )

            # 4. Если передана записка, сохраняем её
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
        self, piggy_bank_id: str, author: Author, text: str
    ) -> PiggyBankNoteModel:
        db: Session = SessionLocal()
        try:
            note = PiggyBankNoteModel(
                id=f"note-{uuid.uuid4().hex[:8]}",
                piggy_bank_id=piggy_bank_id,
                author=author.value,
                text=text,
            )
            db.add(note)
            db.commit()
            db.refresh(note)
            return note
        finally:
            db.close()

    def get_all(self) -> List[PiggyBankModel]:
        db: Session = SessionLocal()
        try:
            return db.query(PiggyBankModel).all()
        finally:
            db.close()

    def get_notes(self, piggy_bank_id: str) -> List[PiggyBankNoteModel]:
        db: Session = SessionLocal()
        try:
            return (
                db.query(PiggyBankNoteModel)
                .filter(PiggyBankNoteModel.piggy_bank_id == piggy_bank_id)
                .order_by(PiggyBankNoteModel.created_at.desc())
                .all()
            )
        finally:
            db.close()

    def delete_piggy_bank(
        self, piggy_bank_id: str, return_funds_to_account: bool = True
    ) -> dict:
        """Безопасное удаление: возвращает накопленные средства обратно на баланс счёта."""
        db: Session = SessionLocal()
        try:
            pb = (
                db.query(PiggyBankModel)
                .filter(PiggyBankModel.id == piggy_bank_id)
                .first()
            )
            if not pb:
                raise KeyError(f"Копилка '{piggy_bank_id}' не найдена")

            current_funds = Decimal(str(pb.current_amount))

            # Если в копилке остались деньги, возвращаем их на счёт
            if return_funds_to_account and current_funds > 0:
                account = self._account_svc.get_account(pb.account_id)
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