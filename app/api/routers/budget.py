from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_budget_service, get_current_user
from app.api.schemas import BudgetForecastResponseSchema
from app.domain.models import Currency
from app.infrastructure.database import UserModel
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budget", tags=["Budget Planning"])


@router.get(
    "/forecast/{category_id}", response_model=BudgetForecastResponseSchema
)
def get_category_budget_forecast(
    category_id: str,
    target_currency: Currency = Query(
        default=Currency.RUB, description="Валюта расчета прогноза"
    ),
    months_back: int = Query(
        default=3, ge=1, le=12, description="Глубина анализа в месяцах (1-12)"
    ),
    current_user: UserModel = Depends(get_current_user),
    svc: BudgetService = Depends(get_budget_service),
):
    forecast = svc.predict_category_budget(
        category_id=category_id,
        target_currency=target_currency,
        months_back=months_back,
        family_group_id=current_user.family_group_id,
    )
    return BudgetForecastResponseSchema(
        category_id=forecast.category_id,
        category_name=forecast.category_name,
        target_currency=forecast.target_currency,
        average_monthly_expense=forecast.average_monthly_expense,
        predicted_next_month=forecast.predicted_next_month,
        months_analyzed=forecast.months_analyzed,
        is_active_next_month=forecast.is_active_next_month,
        explanation=forecast.explanation,
    )