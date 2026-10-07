from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_account_service
from app.api.schemas import TransactionCreateSchema
from app.domain.models import Transaction
from app.services.account_service import AccountService

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_transaction(
    dto: TransactionCreateSchema,
    svc: AccountService = Depends(get_account_service),
):
    try:
        tx = Transaction(
            id=dto.id or str(uuid.uuid4()),
            type=dto.type,
            category_id=dto.category_id,
            amount=dto.amount,
            currency=dto.currency,
            account_id=dto.account_id,
            author=dto.author,
            note=dto.note,
            date=dto.date or datetime.now(),
        )
        svc.add_transaction(tx)
        return {"status": "success", "transaction_id": tx.id}
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))