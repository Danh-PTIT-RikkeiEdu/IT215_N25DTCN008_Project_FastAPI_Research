from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.users import UserCreate
from app.models.users import UsersModel


def create_user(db: Session, user_data: UserCreate):
    # Kiểm tra email
    clean_email = user_data.email.lower().strip() # Validate email người dùng để tạo tài khoản

    existing_user = db.query(UsersModel).filter(UsersModel.email == clean_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại! Vui lòng nhập Email khác"
        )

    