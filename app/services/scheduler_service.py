from datetime import datetime
from decimal import Decimal
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.domain.models import Author
from app.infrastructure.database import (
    CategoryModel,
    PiggyBankModel,
    SessionLocal,
)
from app.services.account_service import AccountService
from app.services.piggy_bank_service import PiggyBankService

logger = logging.getLogger(__name__)


class ScheduledTasksWorker:

    def __init__(
        self, account_svc: AccountService, piggy_svc: PiggyBankService
    ):
        self._account_svc = account_svc
        self._piggy_svc = piggy_svc
        self._scheduler = BackgroundScheduler()

    def start(self):
        """Запуск фонового планировщика раз в сутки в полночь."""
        self._scheduler.add_job(
            self.run_daily_tasks,
            "cron",
            hour=0,
            minute=1,
            id="daily_finance",
            replace_existing=True,
        )
        self._scheduler.start()

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def run_daily_tasks(self):
        """Основной цикл выполнения регулярных задач."""
        today = datetime.utcnow()
        current_day = today.day

        db: Session = SessionLocal()
        try:
            # 1. Автопополнение Копилок (Piggy Banks)
            auto_piggies = (
                db.query(PiggyBankModel)
                .filter(
                    PiggyBankModel.is_auto_replenish == True,
                    PiggyBankModel.is_completed == False,
                    PiggyBankModel.auto_replenish_day == current_day,
                )
                .all()
            )

            for pb in auto_piggies:
                try:
                    self._piggy_svc.deposit(
                        piggy_bank_id=pb.id,
                        amount=Decimal(str(pb.auto_replenish_amount)),
                        author=Author.HUSBAND,
                        note_text=f"Регулярное автопополнение за {current_day} число",
                    )
                except Exception as exc:
                    logger.error(
                        "[Scheduler] Ошибка автопополнения копилки %s: %s",
                        pb.name,
                        exc,
                    )

            # 2. Проверка наступления дат регулярных категорий
            due_categories = (
                db.query(CategoryModel)
                .filter(
                    CategoryModel.frequency == "MONTHLY",
                    CategoryModel.day_of_month == current_day,
                )
                .all()
            )
            for cat in due_categories:
                logger.info(
                    "[Scheduler] Регулярный платёж для категории '%s' наступил сегодня (%d число)",
                    cat.name,
                    current_day,
                )
        finally:
            db.close()