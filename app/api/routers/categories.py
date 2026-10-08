from datetime import datetime
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from app.api.dependencies import get_category_repository, get_current_user
from app.api.schemas import (
    CategoryCreateSchema,
    CategoryResponseSchema,
    CategoryUpdateSchema,
)
from app.domain.interfaces import ICategoryRepository
from app.domain.models import Category, CategoryGroup
from app.infrastructure.database import UserModel

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    dto: CategoryCreateSchema,
    current_user: UserModel = Depends(get_current_user),
    cat_repo: ICategoryRepository = Depends(get_category_repository),
):
    category = Category(
        id=dto.id or f"cat-{uuid.uuid4().hex[:8]}",
        family_group_id=current_user.family_group_id,
        name=dto.name,
        group=dto.group,
        periodicity=dto.periodicity,
        months_duration=dto.months_duration,
        frequency=dto.frequency,
        day_of_month=dto.day_of_month,
        day_of_week=dto.day_of_week,
        recurrence_month=dto.recurrence_month,
        color=dto.color or "#8b5cf6",
        created_at=datetime.utcnow(),
    )
    cat_repo.add(category)
    return category


@router.get("", response_model=List[CategoryResponseSchema])
def get_categories(
    group: Optional[CategoryGroup] = Query(default=None),
    active_year: Optional[int] = Query(default=None),
    active_month: Optional[int] = Query(default=None, ge=1, le=12),
    current_user: UserModel = Depends(get_current_user),
    cat_repo: ICategoryRepository = Depends(get_category_repository),
):
    all_cats = cat_repo.get_all(current_user.family_group_id)
    if group:
        all_cats = [c for c in all_cats if c.group == group]
    if active_year is not None and active_month is not None:
        all_cats = [c for c in all_cats if c.is_active_at(active_year, active_month)]
    return all_cats


@router.put("/{category_id}", response_model=CategoryResponseSchema)
def update_category(
    category_id: str,
    dto: CategoryUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    cat_repo: ICategoryRepository = Depends(get_category_repository),
):
    cat = cat_repo.get_by_id(category_id, current_user.family_group_id)
    if not cat:
        raise KeyError(f"Категория '{category_id}' не найдена")

    if dto.name:
        cat.name = dto.name
    if dto.day_of_month is not None:
        cat.day_of_month = dto.day_of_month
    if dto.day_of_week is not None:
        cat.day_of_week = dto.day_of_week
    if dto.recurrence_month is not None:
        cat.recurrence_month = dto.recurrence_month
    if dto.color is not None:
        cat.color = dto.color

    cat_repo.update(cat)
    return cat


@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(
    category_id: str,
    current_user: UserModel = Depends(get_current_user),
    cat_repo: ICategoryRepository = Depends(get_category_repository),
):
    if not cat_repo.delete(category_id, current_user.family_group_id):
        raise KeyError(f"Категория '{category_id}' не найдена")
    return {
        "status": "success",
        "message": f"Категория {category_id} успешно удалена",
    }