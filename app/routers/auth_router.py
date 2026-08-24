from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.users import UserCreate, UserResponse, TokenResponse, UserLogin
from app.services.auth_service import create_user, login_user
from app.core.responses import success_response


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    new_data = create_user(db, user_data)
    return success_response(
        data=new_data,
        message="Tạo tài khoản mới thành công! Bây giờ bạn có thể đăng nhập",
        request=request
    )


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    new_data = login_user(db, login_data)
    return success_response(
        data=new_data,
        message="Đăng nhập thành công!",
        request=request
    )