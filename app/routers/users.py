from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.users import UsersModel, UserRole
from app.schemas.users import UserResponse
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


def require_admin(current_user: UsersModel = Depends(get_current_user)) -> UsersModel:
    if bool(current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quyền hạn không cho phép!"
        )
    return current_user


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: UsersModel = Depends(get_current_user)):
    return current_user


@router.get("", response_model=List[UserResponse])
def get_all_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    admin_user: UsersModel = Depends(require_admin)
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