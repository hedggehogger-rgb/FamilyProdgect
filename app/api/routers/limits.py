from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_currency_converter, get_current_user
from app.api.schemas import LimitStatusResponseSchema, SetLimitSchema
from app.infrastructure.database import UserModel
from app.services.currency_service import CurrencyConverter
from app.services.limit_service import LimitService

router = APIRouter(prefix="/limits", tags=["Limits"])


def get_limit_service(
    converter: CurrencyConverter = Depends(get_currency_converter),
) -> LimitService:
    return LimitService(converter)


@router.post("", status_code=status.HTTP_201_CREATED)
def set_category_limit(
    dto: SetLimitSchema,
    current_user: UserModel = Depends(get_current_user),
    svc: LimitService = Depends(get_limit_service),
):
    lim = svc.set_limit(
        dto.category_id,
        dto.limit_amount,
        dto.currency,
        dto.months_duration,
        current_user.family_group_id,
    )
    return {"status": "success", "limit_id": lim.id}


@router.get("/status/{category_id}", response_model=LimitStatusResponseSchema)
def get_limit_status(
    category_id: str,
    year: int = Query(..., examples=[2026]),
    month: int = Query(..., ge=1, le=12, examples=[10]),
    current_user: UserModel = Depends(get_current_user),
    svc: LimitService = Depends(get_limit_service),
):
    status_info = svc.get_category_limit_status(
        category_id, year, month, current_user.family_group_id
    )
    if not status_info:
        raise KeyError(f"Лимит для категории '{category_id}' не установлен")
    return status_info