from typing import Any

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.details = details


class BadRequestException(AppHTTPException):
    def __init__(self, message: str = "Bad request", details: Any = None) -> None:
        super().__init__(400, "BAD_REQUEST", message, details)


class ForbiddenException(AppHTTPException):
    def __init__(self, message: str = "Forbidden", details: Any = None) -> None:
        super().__init__(403, "FORBIDDEN", message, details)


class NotFoundException(AppHTTPException):
    def __init__(self, message: str = "Resource not found", details: Any = None) -> None:
        super().__init__(404, "NOT_FOUND", message, details)


def error_response(code: str, message: str, details: Any = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return {"success": False, "error": error}


async def http_exception_handler(
    request: Request, exception: Exception
) -> JSONResponse:
    if isinstance(exception, AppHTTPException):
        code = exception.code
        details = exception.details
    elif isinstance(exception, HTTPException):
        code_by_status = {
            400: "BAD_REQUEST",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
        }
        code = code_by_status.get(exception.status_code, "HTTP_ERROR")
        details = None
    else:
        return JSONResponse(
            status_code=500,
            content=error_response("INTERNAL_SERVER_ERROR", "Internal server error"),
        )

    message = exception.detail if isinstance(exception.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exception.status_code,
        content=error_response(code, message, details),
    )


async def validation_exception_handler(
    request: Request, exception: Exception
) -> JSONResponse:
    details = (
        jsonable_encoder(exception.errors())
        if isinstance(exception, RequestValidationError)
        else None
    )
    return JSONResponse(
        status_code=400,
        content=error_response(
            "VALIDATION_ERROR",
            "Request validation failed",
            details,
        ),
    )