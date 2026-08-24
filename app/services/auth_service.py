from typing import Optional

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Query, Depends

from app.schemas.users import UserCreate, UserLogin
from app.models.users import UsersModel
from app.core.security import hash_password
from app.core.security import verify_password, create_access_token
from app.db.database import get_db
from app.dependencies.permissions import require_admin


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
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def login_user(db: Session, login_data: UserLogin):
    user = db.query(UsersModel).filter(UsersModel.email == login_data.email.lower().strip()).first()
        
    if not user or not verify_password(login_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác!",
            headers={"WWW-Authenticate": "Bearer"},
        )
            
    if not bool(user.is_active):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đang bị khóa hoặc không hoạt động!"
        )
        
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


def get_all_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    _: UsersModel = Depends(require_admin)
):
    query = db.query(UsersModel)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (UsersModel.full_name.ilike(search_term)) | (UsersModel.email.ilike(search_term))
        )
        
    if is_active is not None:
        query = query.filter(UsersModel.is_active == is_active)
        
    return query.all()