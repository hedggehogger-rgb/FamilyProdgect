from decimal import Decimal
from typing import Dict
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_analytics_service, get_currency_converter, get_current_user
from app.api.schemas import MonthlyReportResponseSchema
from app.domain.models import Currency
from app.infrastructure.database import UserModel
from app.services.analytics_service import AnalyticsService
from app.services.currency_service import CurrencyConverter

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/rates", response_model=Dict[str, str])
def get_exchange_rates(converter: CurrencyConverter = Depends(get_currency_converter)):
    return converter.get_all_rates()

@router.get("/monthly-report", response_model=MonthlyReportResponseSchema)
def get_monthly_report(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    currency: Currency = Query(default=Currency.RUB),
    current_user: UserModel = Depends(get_current_user),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    report = svc.get_monthly_report(year, month, currency, current_user.family_group_id)
    return MonthlyReportResponseSchema(
        year=report.year, month=report.month, currency=report.currency,
        total_income=report.total_income, total_expense=report.total_expense, net_savings=report.net_savings,
    )

@router.get("/expenses-by-recurrence", response_model=Dict[str, Decimal])
def get_expenses_by_recurrence(
    year: int = Query(...), month: int = Query(..., ge=1, le=12),
    currency: Currency = Query(default=Currency.RUB),
    current_user: UserModel = Depends(get_current_user),
    svc: AnalyticsService = Depends(get_analytics_service),
):
    return svc.get_expenses_by_recurrence(year, month, currency, current_user.family_group_id)