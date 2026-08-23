from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.schemas.users import UserCreate
from app.models.users import UsersModel
from app.core.security import hash_password

def create_user(db: Session, user_data: UserCreate):
    # Kiểm tra email
    clean_email = user_data.email.lower().strip() # Validate email người dùng để tạo tài khoản

    existing_user = db.query(UsersModel).filter(UsersModel.email == clean_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã tồn tại! Vui lòng nhập Email khác"
        )

    hashed_pw = hash_password(user_data.password)

    new_user = UsersModel(
        email=clean_email,
        password_hash=hashed_pw,
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user