from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn
from app.api.routers import (
    accounts,
    analytics,
    budget,
    categories,
    transactions,
)
from app.core.config import settings
from app.infrastructure.database import init_db

# 1. Создаем экземпляр приложения
app = FastAPI(
    title="Family Finance Backend",
    description="REST API для кроссплатформенного семейного бюджета (Web, Tablet, Mobile)",
    version="1.0.0",
)

# 2. Настраиваем CORS для Vue.js (всегда перед роутерами)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Инициализируем таблицы в PostgreSQL
init_db()


# 4. Глобальные обработчики ошибок
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


# 5. П