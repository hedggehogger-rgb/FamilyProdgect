from datetime import datetime
from decimal import Decimal
import logging
from zoneinfo import ZoneInfo
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
ARMENIA_TZ = ZoneInfo("Asia/Yerevan")


class ScheduledTasksWorker:

    def __init__(
        self, account_svc: AccountService, piggy_svc: PiggyBankService
    ):
        self._account_svc = account_svc
        self._piggy_svc = piggy_svc
        # Планировщик привязан к часовому поясу Армении
        self._scheduler = BackgroundScheduler(timezone="Asia/Yerevan")

    def start(self):
        # Запуск каждый день ровно в 20:00 по времени Армении
        self._scheduler.add_job(
            self.run_daily_tasks,
            "cron",
            hour=20,
            minute=0,
            timezone="Asia/Yerevan",
            id="daily_finance",
            replace_existing=True,
        )
        self._scheduler.start()
        logger.info("[Scheduler] Планировщик запущен: выполнение ежедневно в 20:00 (Asia/Yerevan)")

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def run_daily_tasks(self):
        # Текущая дата и время строго по часовому поясу Армении
        now_am = datetime.now(ARMENIA_TZ)
        today = now_am.replace(tzinfo=None)
        current_day = today.day
        current_ym = f"{today.year:04d}-{today.month:02d}"

        logger.info(f"[Scheduler] Старт ежедневных задач за {today.date()} (20:00 Asia/Yerevan)")

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

            # 3. Удаление категорий с истекшим сроком действия ("срок годности")
            expired_categories = (
                db.query(CategoryModel)
                .filter(
                    CategoryModel.expires_at.isnot(None),
                    CategoryModel.expires_at <= today,
                )
                .all()
            )
            for exp_cat in expired_categories:
                try:
                    db.delete(exp_cat)
                    db.commit()
                    logger.info(f"[Scheduler] Категория '{exp_cat.name}' удалена по истечении срока действия.")
                except Exception as exc:
                    logger.error(f"[Scheduler] Ошибка удаления просроченной категории {exp_cat.name}: {exc}")

        finally:
            db.close()