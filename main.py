from fastapi import FastAPI, Request  # Depends
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from database import engine, Base  # get_db
from app.routers import participants
from app.routers import science

# Создаем таблицы в БД при запуске (для простоты)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Conference Management API")


# --- Задание 6: Служебный адрес проверки работоспособности (Health Check) ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "conference-api"}


# --- Задание 6: Глобальная обработка некорректных запросов/ошибок БД ---
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка базы данных. Попробуйте позже."},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."},
    )


@app.get("/")
def root():
    return {"message": "Welcome to Conference API. Go to /docs for Swagger UI"}


app.include_router(science.router)
app.include_router(participants.router)
