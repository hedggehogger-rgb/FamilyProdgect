from datetime import datetime
from typing import List
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_account_service
from app.api.schemas import (
    TransactionCreateSchema,
    TransactionResponseSchema,
    TransferCreateSchema,
)
from app.domain.models import Transaction, TransactionType
from app.services.account_service import AccountService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_transaction(
    dto: TransactionCreateSchema,
    svc: AccountService = Depends(get_account_service),
):
    tx = Transaction(
        id=dto.id or str(uuid.uuid4()),
        type=dto.type,
        category_id=dto.category_id,
        amount=dto.amount,
        currency=dto.currency,
        account_id=dto.account_id,
        to_account_id=dto.to_account_id,
        author=dto.author,
        note=dto.note,
        date=dto.date or datetime.utcnow(),
    )
    svc.add_transaction(tx)
    return {"status": "success", "transaction_id": tx.id}


@router.post("/transfer", status_code=status.HTTP_201_CREATED)
def transfer_between_accounts(
    dto: TransferCreateSchema,
    svc: AccountService = Depends(get_account_service),
):
    tx = Transaction(
        id=str(uuid.uuid4()),
        type=TransactionType.TRANSFER,
        category_id=None,
        amount=dto.amount,
        currency=dto.currency,
        account_id=dto.from_account_id,
        to_account_id=dto.to_account_id,
        author=dto.author,
        note=dto.note,
        date=datetime.utcnow(),
    )
    svc.add_transaction(tx)
    return {
        "status": "success",
        "message": f"Переведено {dto.amount} {dto.currency.value} со счёта {dto.from_account_id} на {dto.to_account_id}",
        "transaction_id": tx.id,
    }


@router.get("", response_model=List[TransactionResponseSchema])
def get_all_transactions(svc: AccountService = Depends(get_account_service)):
    return svc._tx_repo.get_all()


@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
def delete_transaction(
    transaction_id: str, svc: AccountService = Depends(get_account_service)
):
    svc.delete_transaction(transaction_id)
    return {
        "status": "success",
        "message": f"Транзакция {transaction_id} удалена, баланс счёта успешно восстановлен",
    }