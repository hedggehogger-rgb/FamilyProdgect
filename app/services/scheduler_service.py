from datetime import datetime
from decimal import Decimal
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.domain.models import Author, Currency, Transaction, TransactionType
from app.infrastructure.database import (
    CategoryModel,
    PiggyBankModel,
    SessionLocal,
    TransactionModel,
)
from app.services.account_service import AccountService
from app.services.piggy_bank_service import PiggyBankService


class ScheduledTasksWorker:

    def __init__(
        self, account_svc: AccountService, piggy_svc: PiggyBankService
    ):
        self._account_svc = account_svc
        self._piggy_svc = piggy_svc
        self._scheduler = BackgroundScheduler()

    def start(self):
        """Запускает фонового демона проверки платежей раз в сутки в полночь."""
        self._scheduler.add_job(
            self.run_daily_tasks, "cron", hour=0, minute=1, id="daily_finance"
        )
        self._scheduler.start()

    def run_daily_tasks(self):
        """Основной цикл проверки регулярных категорий и копилок."""
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
                        author=Author.HUSBAND,  # Системное автосписание
                        note_text=f"Регулярное автопополнение за {current_day} число",
                    )
                except Exception as e:
                    print(
                        f"[Scheduler] Ошибка автопополнения копилки {pb.name}: {e}"
                    )

            # 2. Автоматическое создание регулярных транзакций по категориям (например, интернет 1-го числа)
            auto_categories = (
                db.query(CategoryModel)
                .filter(
                    CategoryModel.frequency == "MONTHLY",
                    CategoryModel.day_of_month == current_day,
                )
                .all()
            )

            accounts = self._account_svc._account_repo.find_all()
            if accounts:
                main_acc = accounts[0]
                for cat in auto_categories:
                    # Создаем запись, чтобы пользователь мог её отредактировать или удалить
                    pass

        finally:
            db.close()