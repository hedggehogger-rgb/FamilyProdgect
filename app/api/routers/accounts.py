from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_account_service
from app.api.schemas import AccountCreateSchema, AccountResponseSchema
from app.domain.models import Account
from app.services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_account(
    dto: AccountCreateSchema,
    svc: AccountService = Depends(get_account_service),
):
    try:
        acc = Account(
            id=dto.id,
            name=dto.name,
            currency=dto.currency,
            balance=dto.balance,
            is_investment=dto.is_investment,
        )
        svc.create_account(acc)
        return {"status": "success", "id": acc.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# <-- ВОТ ЭТОТ ЭНДПОИНТ ДЛЯ VUE: получить все счета
@router.get("", response_model=List[AccountResponseSchema])
def get_all_accounts(svc: AccountService = Depends(get_account_service)):
    accounts = svc._account_repo.find_all()
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
    account_id: str, svc: AccountService = Depends(get_account_service)
):
    try:
        acc = svc.get_account(account_id)
        return AccountResponseSchema(
            id=acc.id,
            name=acc.name,
            currency=acc.currency,
            balance=acc.balance,
            is_investment=acc.is_investment,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Счёт не найден")