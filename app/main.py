from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.db.database import Base, engine
from app import models
from app.core.responses import success_response, failure_response


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="RESEARCH GROUP MANAGEMENT API",
    description="Dự án nhỏ về FastAPI để luyện tay",
    version="1.0.0"
)


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return failure_response(
        errors=None,
        message=exc.detail,
        request=request,
        status_code=exc.status_code
    )


@app.get("/")
def try_connect():
    return "Kết nối thành công"


@app.get("/health")
def health_check(request: Request):
    return success_response(
        data={"status": "ok"},
        message="Service is healthy",
        request=request
    )