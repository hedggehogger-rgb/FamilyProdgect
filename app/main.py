from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
import uvicorn
from app.api.routers import accounts, analytics, categories, transactions
from app.core.config import settings
from app.infrastructure.database import init_db

app = FastAPI(
    title="Family Finance Backend",
    description="REST API для кроссплатформенного семейного бюджета (Web, Tablet, Mobile)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# --- ГЛОБАЛЬНЫЕ ОБРАБОТЧИКИ ОШИБОК ---


# Перехватывает бизнес-ошибки домена (например, "Недостаточно средств", "Счёт уже существует")
@app.exception_handler(ValueError)
def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


# Перехватывает ошибки отсутствия сущностей ("Счет не найден")
@app.exception_handler(KeyError)
def key_error_handler(request: Request, exc: KeyError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc).strip("'")},
    )


# Подключение роутеров
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(analytics.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "env": settings.APP_ENV}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=(settings.APP_ENV == "development"),
    )