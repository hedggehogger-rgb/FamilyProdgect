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
    TransactionModel,
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
        today = datetime.utcnow()
        current_day = today.day
        current_ym = f"{today.year:04d}-{today.month:02d}"

        db: Session = SessionLocal()
        try:
            # 1. Автопополнение копилок
            auto_piggies = (
                db.query(PiggyBankModel)
                .filter(
                    PiggyBankModel.is_auto_replenish == True,
                    PiggyBankModel.is_completed == False,
                )
                .all()
            )

            for pb in auto_piggies:
                if pb.skip_until_month == current_ym:
                    continue

                should_run = False
                if pb.snoozed_until:
                    if pb.snoozed_until.date() == today.date():
                        should_run = True
                        pb.snoozed_until = None
                        db.commit()
                    elif pb.snoozed_until.date() > today.date():
                        continue
                elif pb.auto_replenish_day == current_day:
                    should_run = True

                if should_run:
                    try:
                        self._piggy_svc.deposit(
                            piggy_bank_id=pb.id,
                            amount=Decimal(str(pb.auto_replenish_amount)),
                            account_id=pb.account_id,
                            author=Author.HUSBAND,
                            note_text=f"Ушло в копилку '{pb.name}'",
                            family_group_id=pb.family_group_id,
                        )
                        logger.info(f"[Scheduler] Успешное автопополнение копилки: {pb.name}")
                    except Exception as exc:
                        logger.error(f"[Scheduler] Ошибка автопополнения {pb.name}: {exc}")

            # 2. Исполнение отложенных разовых платежей, дата которых наступила
            due_deferred_txs = (
                db.query(TransactionModel)
                .filter(
                    TransactionModel.is_executed == False,
                    TransactionModel.date <= today,
                )
                .all()
            )
            for dtx in due_deferred_txs:
                try:
                    self._account_svc.execute_deferred_transaction(
                        dtx.id, dtx.family_group_id
                    )
                    logger.info(f"[Scheduler] Исполнен отложенный платёж: {dtx.id} ({dtx.amount} {dtx.currency})")
                except Exception as exc:
                    logger.error(f"[Scheduler] Ошибка исполнения платежа {dtx.id}: {exc}")

        finally:
            db.close()