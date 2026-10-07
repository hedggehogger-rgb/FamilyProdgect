from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn
from app.api.dependencies import account_service, currency_converter
from app.api.routers import (
    accounts,
    analytics,
    auth,
    budget,
    categories,
    limits,
    piggy_banks,
    transactions,
)
from app.core.config import settings
from app.infrastructure.database import init_db
from app.services.piggy_bank_service import PiggyBankService
from app.services.scheduler_service import ScheduledTasksWorker

# 1. Создаем экземпляр приложения
app = FastAPI(
    title="Family Finance Backend",
    description="REST API для семейного бюджета (Web / Vue.js, Tablet, Mobile)",
    version="1.0.0",
)

# 2. CORS (для Vue 3 / Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Инициализация таблиц в PostgreSQL
init_db()

# 4. Запуск фонового планировщика автоплатежей и копилок
piggy_svc = PiggyBankService(account_service, currency_converter)
scheduler_worker = ScheduledTasksWorker(account_service, piggy_svc)
scheduler_worker.start()


# 5. Глобальные обработчики ошибок
@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


@app.exception_handler(KeyError)
def key_error_handler(request: Request, exc: KeyError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc).strip("'")},
    )


# 6. Подключаем все роутеры приложения
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(budget.router)
app.include_router(limits.router)
app.include_router(piggy_banks.router)


# 7. Служебные эндпоинты
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "env": settings.APP_ENV}


@app.post("/system/run-scheduled-tasks", tags=["System"])
def trigger_scheduled_tasks():
    """Принудительный вызов фоновых платежей (для тестов, не дожидаясь полуночи)."""
    scheduler_worker.run_daily_tasks()
    return {
        "status": "success",
        "message": "Фоновые автоплатежи успешно выполнены",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=(settings.APP_ENV == "development"),
    )