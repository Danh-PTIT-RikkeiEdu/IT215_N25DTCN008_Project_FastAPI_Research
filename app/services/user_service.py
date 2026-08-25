from typing import Optional

from sqlalchemy.orm import Session
from fastapi import Query, Depends

from app.models.users import UsersModel
from app.db.database import get_db
from app.dependencies.permissions import require_admin


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

