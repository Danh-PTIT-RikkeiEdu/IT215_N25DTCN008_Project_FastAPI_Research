from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.users import UsersModel
from app.schemas.users import UserResponse
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_admin
from app.services.auth_service import get_all_users


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: UsersModel = Depends(get_current_user)):
    return current_user


@router.get("", response_model=List[UserResponse])
def list_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    _: UsersModel = Depends(require_admin),
):
    return get_all_users(search=search, is_active=is_active, db=db)