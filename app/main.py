from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from app.api.routers import accounts, analytics, categories, transactions
from app.core.config import settings
from app.infrastructure.database import init_db

# 1. Сначала создаем экземпляр приложения
app = FastAPI(
    title="Family Finance Backend",
    description="REST API для кроссплатформенного семейного бюджета (Web, Tablet, Mobile)",
    version="1.0.0",
)

# 2. Настраиваем CORS для Vue.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

# 3. И только ТЕПЕРЬ подключаем все роутеры к созданному app
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(analytics.router)


# 4. Перенаправление на Swagger при клике из консоли
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "env": settings.APP_ENV}


# 5. Точка запуска сервера
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=(settings.APP_ENV == "development"),
    )