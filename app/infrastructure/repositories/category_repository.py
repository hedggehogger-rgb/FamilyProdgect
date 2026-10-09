from decimal import Decimal
from typing import List, Optional
from app.domain.interfaces import ICategoryRepository
from app.domain.models import (
    DEFAULT_CATEGORY_COLOR,
    Category,
    CategoryGroup,
    CategoryPeriodicity,
    RecurrenceFrequency,
)
from app.infrastructure.database import CategoryModel
from app.infrastructure.repositories.base import BasePostgresRepository


class PostgresCategoryRepository(BasePostgresRepository, ICategoryRepository):

    def add(self, category: Category) -> None:
        self.update(category)

    def update(self, category: Category) -> None:
        with self._get_db() as db:
            model = CategoryModel(
                id=category.id,
                family_group_id=category.family_group_id,
                name=category.name,
                group=category.group.value,
                periodicity=category.periodicity.value,
                months_duration=category.months_duration,
                frequency=category.frequency.value,
                day_of_month=category.day_of_month,
                day_of_week=category.day_of_week,
                recurrence_month=category.recurrence_month,
                color=category.color,
                default_amount=category.default_amount,
                default_account_id=category.default_account_id,
                created_at=category.created_at,
            )
            db.merge(model)
            db.commit()

    def get_by_id(
        self, category_id: str, family_group_id: Optional[str] = None
    ) -> Optional[Category]:
        with self._get_db() as db:
            q = db.query(CategoryModel).filter(CategoryModel.id == category_id)
            if family_group_id:
                q = q.filter(CategoryModel.family_group_id == family_group_id)
            row = q.first()
            return self._to_domain(row) if row else None

    def get_all(self, family_group_id: Optional[str] = None) -> List[Category]:
        with self._get_db() as db:
            q = db.query(CategoryModel)
            if family_group_id:
                q = q.filter(CategoryModel.family_group_id == family_group_id)
            return [self._to_domain(r) for r in q.all()]

    def delete(
        self, category_id: str, family_group_id: Optional[str] = None
    ) -> bool:
        with self._get_db() as db:
            q = db.query(CategoryModel).filter(CategoryModel.id == category_id)
            if family_group_id:
                q = q.filter(CategoryModel.family_group_id == family_group_id)
            deleted = q.delete()
            db.commit()
            return deleted > 0

    @staticmethod
    def _to_domain(row: CategoryModel) -> Category:
        return Category(
            id=row.id,
            name=row.name,
            group=CategoryGroup(row.group),
            periodicity=CategoryPeriodicity(row.periodicity),
            months_duration=row.months_duration,
            frequency=RecurrenceFrequency(row.frequency),
            day_of_month=row.day_of_month,
            day_of_week=getattr(row, "day_of_week", None),
            recurrence_month=getattr(row, "recurrence_month", None),
            color=getattr(row, "color", DEFAULT_CATEGORY_COLOR) or DEFAULT_CATEGORY_COLOR,
            default_amount=Decimal(str(row.default_amount)) if row.default_amount else None,
            default_account_id=row.default_account_id,
            family_group_id=row.family_group_id,
            created_at=row.created_at,
        )