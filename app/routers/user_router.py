from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.users import UsersModel
from app.schemas.users import UserResponse
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_admin
from app.services.user_service import get_all_users
from app.core.responses import success_response, APIResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse)
def get_my_profile(request: Request, current_user: UsersModel = Depends(get_current_user)):
    return success_response(
        data=UserResponse.model_validate(current_user),
        message="Lấy thông tin cá nhân thành công",
        request=request
    )


@router.get("", response_model=APIResponse)
def list_users(
    request: Request,
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    _: UsersModel = Depends(require_admin),
):
    users_data = get_all_users(search=search, is_active=is_active, db=db)
    return success_response(
        data=[UserResponse.model_validate(u) for u in users_data],
        message="Lấy danh sách người dùng thành công",
        request=request
    )