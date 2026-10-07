from typing import List
from fastapi import APIRouter, Depends, status
from app.api.dependencies import get_account_service, get_current_user
from app.api.schemas import AccountCreateSchema, AccountResponseSchema
from app.domain.models import Account
from app.infrastructure.database import UserModel
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_account(
    dto: AccountCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: AccountService = Depends(get_account_service),
):
    acc = Account(
        id=dto.id,
        name=dto.name,
        currency=dto.currency,
        balance=dto.balance,
        is_investment=dto.is_investment,
        family_group_id=current_user.family_group_id,
    )
    svc.create_account(acc)
    return {"status": "success", "id": acc.id}


@router.get("", response_model=List[AccountResponseSchema])
def get_all_accounts(
    current_user: UserModel = Depends(get_current_user),
    svc: AccountService = Depends(get_account_service),
):
    accounts = svc.get_all_accounts(current_user.family_group_id)
    return [
        AccountResponseSchema(
            id=acc.id,
            name=acc.name,
            currency=acc.currency,
            balance=acc.balance,
            is_investment=acc.is_investment,
        )
        for acc in accounts
    ]


@router.get("/{account_id}", response_model=AccountResponseSchema)
def get_account(
    account_id: str,
    current_user: UserModel = Depends(get_current_user),
    svc: AccountService = Depends(get_account_service),
):
    acc = svc.get_account(account_id, current_user.family_group_id)
    return AccountResponseSchema(
        id=acc.id,
        name=acc.name,
        currency=acc.currency,
        balance=acc.balance,
        is_investment=acc.is_investment,
    )