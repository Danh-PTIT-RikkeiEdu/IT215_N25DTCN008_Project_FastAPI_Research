from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.db.database import Base, engine
from app import models
from app.core.exceptions import http_exception_handler, validation_exception_handler

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RESEARCH GROUP MANAGEMENT API",
    description="Dự án nhỏ về FastAPI để luyện tay",
    version="1.0.0"
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(400, http_exception_handler)
app.add_exception_handler(403, http_exception_handler)
app.add_exception_handler(404, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

@app.get("/")
def try_connect():
    return {"message": "Kết nối thành công"}


@app.get("/health")
def health_check():
    return {"status": "ok"}