from typing import Optional, Any
from datetime import datetime, timezone

from pydantic import BaseModel, Field
from fastapi import Request
from fastapi.responses import JSONResponse


class APIResponse(BaseModel):
    success: bool
    statusCode: int
    message: str
    data: Optional[Any] = None
    errors: Optional[Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    # Dùng Field có default_factory để python hiểu mình đang nhận 1 hàm động
    # Khi nó được gọi đến hàm động sẽ được chạy và chuyển về kdl str
    # Nếu không có Field mà str = lambda thì sẽ sinh ra lỗi 
    # str = lambda, xung đột kiểu dữ liệu str và hàm lại bằng nhau
    path: str


def success_response(data: Any, message: str, request: Request, status_code: int = 200) -> APIResponse:
    return APIResponse(
        success=True,
        statusCode=status_code,
        message=message,
        data=data,
        errors=None,
        path=request.url.path
    )


def failure_response(errors: Any, message: str, request: Request, status_code: int = 400):
    body = APIResponse(
        success=False,
        statusCode=status_code,
        message=message,
        data=None,
        errors=errors,
        path=request.url.path
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())