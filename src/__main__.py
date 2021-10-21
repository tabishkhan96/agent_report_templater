import uvicorn
import logging
from dynaconf import settings

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.repository.exceptions import AppException
from src.views import report_api


logger: logging.Logger = logging.getLogger("app")

app: FastAPI = FastAPI(**settings.APP or {})
app.include_router(report_api, prefix='/report')


@app.exception_handler(AppException)
def client_exc_handler(request: Request, exc: AppException):
    """Обработка исключений приложения"""
    exc_message = next(exc.args, '')
    logger.exception(exc.__doc__)
    return JSONResponse(status_code=400, content={"detail": f"{exc.__doc__}. {exc_message}"})


@app.exception_handler(Exception)
def unexpected_exc_handler(request: Request, exc: Exception):
    logger.exception(exc)
    return JSONResponse(
        status_code=500, content={"detail": "Непредвиденная ошибка сервера. Обратитесь к разработчику."}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ORIGINS or "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

uvicorn.run(app=app, host=settings.SERVICE_HOST, port=settings.SERVICE_PORT)
