from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.users import UserCreate, UserResponse, TokenResponse, UserLogin
from app.services.auth_service import create_user, login_user
from app.core.responses import success_response, APIResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    new_data = create_user(db=db, user_data=user_data)
    return success_response(
        data=UserResponse.model_validate(new_data),
        message="Tạo tài khoản thành công!",
        request=request,
        status_code=status.HTTP_201_CREATED
    )


@router.post("/login", response_model=APIResponse)
def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    new_data = login_user(db=db, login_data=login_data)
    return success_response(
        data=TokenResponse.model_validate(new_data),
        message="Đăng nhập thành công!",
        request=request
    )

