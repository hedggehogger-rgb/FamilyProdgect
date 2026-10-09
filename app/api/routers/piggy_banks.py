from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_account_service, get_currency_converter, get_current_user
from app.api.schemas import (
    PiggyBankAutoReplenishToggleSchema,
    PiggyBankCreateSchema,
    PiggyBankDepositSchema,
    PiggyBankNoteCreateSchema,
    PiggyBankNoteResponseSchema,
    PiggyBankResponseSchema,
    PiggyBankSnoozeSchema,
)
from app.domain.models import Author
from app.infrastructure.database import UserModel
from app.services.account_service import AccountService
from app.services.currency_service import CurrencyConverter
from app.services.piggy_bank_service import PiggyBankService

router = APIRouter(prefix="/piggy-banks", tags=["Piggy Banks (Копилки)"])


def get_piggy_bank_service(
    account_svc: AccountService = Depends(get_account_service),
    converter: CurrencyConverter = Depends(get_currency_converter),
) -> PiggyBankService:
    return PiggyBankService(account_svc, converter)


@router.post("", response_model=PiggyBankResponseSchema, status_code=status.HTTP_201_CREATED)
def create_piggy_bank(
    dto: PiggyBankCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.create_piggy_bank(
        name=dto.name, target_amount=dto.target_amount, account_id=dto.account_id,
        currency=dto.currency, deadline=dto.deadline, is_auto_replenish=dto.is_auto_replenish,
        auto_replenish_amount=dto.auto_replenish_amount, auto_replenish_day=dto.auto_replenish_day,
        family_group_id=current_user.family_group_id,
    )


@router.get("", response_model=List[PiggyBankResponseSchema])
def get_all_piggy_banks(
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.get_all(current_user.family_group_id)


@router.post("/{piggy_bank_id}/deposit", response_model=PiggyBankResponseSchema)
def deposit_to_piggy_bank(
    piggy_bank_id: str,
    dto: PiggyBankDepositSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    author = Author(current_user.role)
    return svc.deposit(
        piggy_bank_id=piggy_bank_id,
        amount=dto.amount,
        account_id=dto.account_id,
        author=author,
        deposit_currency=dto.currency,
        note_text=dto.note,
        family_group_id=current_user.family_group_id,
    )


# Поддерживаем и POST, и PATCH для надежности
@router.post("/{piggy_bank_id}/auto-replenish", response_model=PiggyBankResponseSchema)
@router.patch("/{piggy_bank_id}/auto-replenish", response_model=PiggyBankResponseSchema)
def toggle_auto_replenish(
    piggy_bank_id: str,
    dto: PiggyBankAutoReplenishToggleSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.toggle_auto_replenish(
        piggy_bank_id=piggy_bank_id,
        is_auto_replenish=dto.is_auto_replenish,
        amount=dto.auto_replenish_amount,
        day=dto.auto_replenish_day,
        account_id=dto.account_id,
        family_group_id=current_user.family_group_id,
    )


@router.post("/{piggy_bank_id}/snooze", response_model=PiggyBankResponseSchema)
def snooze_auto_replenish(
    piggy_bank_id: str,
    dto: PiggyBankSnoozeSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.snooze_auto_replenish(
        piggy_bank_id=piggy_bank_id,
        snooze_date=dto.snooze_date,
        skip_current_month=dto.skip_current_month,
        family_group_id=current_user.family_group_id,
    )


@router.post("/{piggy_bank_id}/notes", response_model=PiggyBankNoteResponseSchema)
def add_note_to_piggy_bank(
    piggy_bank_id: str, dto: PiggyBankNoteCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    author = Author(current_user.role)
    return svc.add_note(piggy_bank_id, author, dto.text, current_user.family_group_id)


@router.get("/{piggy_bank_id}/notes", response_model=List[PiggyBankNoteResponseSchema])
def get_piggy_bank_notes(
    piggy_bank_id: str,
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.get_notes(piggy_bank_id, current_user.family_group_id)


@router.delete("/{piggy_bank_id}")
def delete_piggy_bank(
    piggy_bank_id: str,
    target_account_id: Optional[str] = Query(default=None),
    current_user: UserModel = Depends(get_current_user),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    author = Author(current_user.role)
    return svc.delete_piggy_bank(
        piggy_bank_id,
        target_account_id=target_account_id,
        author=author,
        family_group_id=current_user.family_group_id,
    )