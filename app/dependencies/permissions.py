from fastapi import APIRouter, Depends, HTTPException, status

from app.models.users import UsersModel, UserRole
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


def require_admin(current_user: UsersModel = Depends(get_current_user)) -> UsersModel:
    if bool(current_user.role != UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Quyền hạn không cho phép!"
        )
    return current_user
