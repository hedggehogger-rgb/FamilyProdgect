from typing import List
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_account_service, get_currency_converter
from app.api.schemas import (
    PiggyBankCreateSchema,
    PiggyBankDepositSchema,
    PiggyBankNoteCreateSchema,
    PiggyBankNoteResponseSchema,
    PiggyBankResponseSchema,
)
from app.domain.models import Currency
from app.services.account_service import AccountService
from app.services.currency_service import CurrencyConverter
from app.services.piggy_bank_service import PiggyBankService

router = APIRouter(prefix="/piggy-banks", tags=["Piggy Banks (Копилки)"])


def get_piggy_bank_service(
    account_svc: AccountService = Depends(get_account_service),
    converter: CurrencyConverter = Depends(get_currency_converter),
) -> PiggyBankService:
    return PiggyBankService(account_svc, converter)


@router.post(
    "",
    response_model=PiggyBankResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_piggy_bank(
    dto: PiggyBankCreateSchema,
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.create_piggy_bank(
        name=dto.name,
        target_amount=dto.target_amount,
        account_id=dto.account_id,
        currency=dto.currency,
        deadline=dto.deadline,
        is_auto_replenish=dto.is_auto_replenish,
        auto_replenish_amount=dto.auto_replenish_amount,
        auto_replenish_day=dto.auto_replenish_day,
    )


@router.get("", response_model=List[PiggyBankResponseSchema])
def get_all_piggy_banks(
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.get_all()


@router.post("/{piggy_bank_id}/deposit", response_model=PiggyBankResponseSchema)
def deposit_to_piggy_bank(
    piggy_bank_id: str,
    dto: PiggyBankDepositSchema,
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.deposit(piggy_bank_id, dto.amount, dto.author, dto.note)


@router.post(
    "/{piggy_bank_id}/notes", response_model=PiggyBankNoteResponseSchema
)
def add_note_to_piggy_bank(
    piggy_bank_id: str,
    dto: PiggyBankNoteCreateSchema,
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.add_note(piggy_bank_id, dto.author, dto.text)


@router.get(
    "/{piggy_bank_id}/notes", response_model=List[PiggyBankNoteResponseSchema]
)
def get_piggy_bank_notes(
    piggy_bank_id: str,
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.get_notes(piggy_bank_id)


@router.delete("/{piggy_bank_id}")
def delete_piggy_bank(
    piggy_bank_id: str,
    return_funds: bool = Query(
        default=True,
        description="Вернуть накопленные средства обратно на счёт",
    ),
    svc: PiggyBankService = Depends(get_piggy_bank_service),
):
    return svc.delete_piggy_bank(
        piggy_bank_id, return_funds_to_account=return_funds
    )