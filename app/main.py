from fastapi import FastAPI


app = FastAPI(
    title="RESEARCH GROUP MANAGEMENT API",
    description="Dự án nhỏ về FastAPI để luyện tay",
    version="1.0.0"
)

@app.get("/")
def try_connect():
    return {"message": "Kết nối thành công"}