from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import (
    get_account_service,
    get_current_user,
    get_transaction_repo,
)
from app.api.schemas import (
    ActionStatusResponse,
    PaginatedResponse,
    TransactionCreateSchema,
    TransactionResponseSchema,
    TransferCreateSchema,
)
from app.domain.models import Author, Transaction
from app.infrastructure.database import UserModel
from app.infrastructure.repositories import PostgresTransactionRepository
from app.services.account_service import AccountService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post(
    "",
    response_model=ActionStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_transaction(
    dto: TransactionCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: AccountService = Depends(get_account_service),
):
    svc.get_account(dto.account_id, current_user.family_group_id)
    if dto.to_account_id:
        svc.get_account(dto.to_account_id, current_user.family_group_id)

    author = Author(current_user.role)
    tx = Transaction(
        id=dto.id or str(uuid.uuid4()),
        family_group_id=current_user.family_group_id,
        type=dto.type,
        category_id=dto.category_id,
        amount=dto.amount,
        currency=dto.currency,
        account_id=dto.account_id,
        to_account_id=dto.to_account_id,
        author=author,
        note=dto.note,
        date=dto.date or datetime.utcnow(),
    )
    svc.add_transaction(tx)
    return ActionStatusResponse(
        message="Транзакция успешно сохранена", id=tx.id
    )


@router.post(
    "/transfer",
    response_model=ActionStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def transfer_between_accounts(
    dto: TransferCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: AccountService = Depends(get_account_service),
):
    tx = svc.transfer_funds(
        from_account_id=dto.from_account_id,
        to_account_id=dto.to_account_id,
        amount=dto.amount,
        author=Author(current_user.role),
        family_group_id=current_user.family_group_id,
        note=dto.note,
    )
    return ActionStatusResponse(
        message=f"Переведено {dto.amount} {dto.currency.value}",
        id=tx.id,
    )


@router.get("", response_model=PaginatedResponse[TransactionResponseSchema])
def get_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    account_id: Optional[str] = Query(default=None),
    category_id: Optional[str] = Query(default=None),
    current_user: UserModel = Depends(get_current_user),
    tx_repo: PostgresTransactionRepository = Depends(get_transaction_repo),
):
    items, total = tx_repo.get_paginated(
        family_group_id=current_user.family_group_id,
        limit=limit,
        offset=offset,
        account_id=account_id,
        category_id=category_id,
    )
    return PaginatedResponse(
        items=[
            TransactionResponseSchema(
                id=t.id,
                type=t.type,
                category_id=t.category_id,
                amount=t.amount,
                currency=t.currency,
                account_id=t.account_id,
                to_account_id=t.to_account_id,
                author=t.author,
                note=t.note,
                date=t.date,
            )
            for t in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{transaction_id}", response_model=ActionStatusResponse)
def delete_transaction(
    transaction_id: str,
    current_user: UserModel = Depends(get_current_user),
    svc: AccountService = Depends(get_account_service),
):
    svc.delete_transaction(transaction_id, current_user.family_group_id)
    return ActionStatusResponse(
        message=f"Транзакция {transaction_id} удалена, баланс счёта восстановлен",
        id=transaction_id,
    )