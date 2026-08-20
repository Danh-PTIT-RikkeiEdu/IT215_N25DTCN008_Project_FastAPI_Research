from fastapi import FastAPI
from app.db.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RESEARCH GROUP MANAGEMENT API",
    description="Dự án nhỏ về FastAPI để luyện tay",
    version="1.0.0"
)

@app.get("/")
def try_connect():
    return {"message": "Kết nối thành công"}