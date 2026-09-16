from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from database import engine, Base
from app.routers import participants
from app.routers import science
from app.routers import org

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Conference Management API")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Служебный адрес проверки работоспособности (Health Check)
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "conference-api"}


# Глобальная обработка некорректных запросов/ошибок БД
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


@app.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


app.include_router(science.router)
app.include_router(participants.router)
app.include_router(org.router)
