from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.api.dependencies import get_category_repository
from app.domain.interfaces import ICategoryRepository
from app.domain.models import (
    Category,
    CategoryGroup,
    CategoryPeriodicity,
    RecurrenceFrequency,
)

router = APIRouter(prefix="/categories", tags=["Categories"])


class CategoryResponseSchema(BaseModel):
    id: str
    name: str
    group: CategoryGroup
    periodicity: CategoryPeriodicity
    frequency: RecurrenceFrequency


@router.get("", response_model=List[CategoryResponseSchema])
def get_all_categories(
    cat_repo: ICategoryRepository = Depends(get_category_repository),
):
    categories = cat_repo.get_all()
    return [
        CategoryResponseSchema(
            id=cat.id,
            name=cat.name,
            group=cat.group,
            periodicity=cat.periodicity,
            frequency=cat.frequency,
        )
        for cat in categories
    ]