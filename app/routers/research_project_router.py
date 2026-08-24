from typing import List, Optional

from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.orm import Session

from app.schemas.research_projects import ResearchProjectResponse, ResearchProjectCreate, ResearchProjectUpdate
from app.schemas.research_members import ResearchMemberResponse, ResearchMemberCreate
from app.services.research_project_service import (
    create_research_project, 
    get_research_projects,
    get_research_project_by_id,
    update_research_project,
    delete_research_project,
    add_member_to_project,
    remove_member_from_project,
    get_project_members
)
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import UsersModel
from app.core.responses import success_response


router = APIRouter(prefix="/research-projects", tags=["Research Projects"])


@router.post("", response_model=ResearchProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    research_project_data: ResearchProjectCreate, 
    request: Request, 
    current_user: UsersModel = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    new_data = create_research_project(
        db,
        research_project_data,
        owner_id=int(current_user.id)
    )
    return success_response(
        data=new_data,
        message="Tạo đề tài nghiên cứu thành công",
        request=request,
        status_code=status.HTTP_201_CREATED
    )

@router.get("", response_model=List[ResearchProjectResponse], status_code=status.HTTP_200_OK)
def get_projects(
    search: Optional[str] = Query(None),
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    projects = get_research_projects(
        db=db,
        user_id=int(current_user.id),
        search_name=search
    )
    return projects

@router.get("/{id}", response_model=ResearchProjectResponse, status_code=status.HTTP_200_OK)
def get_project_by_id(
    id: int,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_research_project_by_id(db, id, int(current_user.id))

@router.patch("/{id}", response_model=ResearchProjectResponse, status_code=status.HTTP_200_OK)
def update_project(
    id: int,
    project_data: ResearchProjectUpdate,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_project = update_research_project(db, id, project_data, int(current_user.id))
    return success_response(
        data=updated_project,
        message="Cập nhật đề tài nghiên cứu thành công",
        request=request
    )

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_project(
    id: int,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delete_research_project(db, id, int(current_user.id))
    return success_response(
        data=None,
        message="Xóa đề tài nghiên cứu thành công",
        request=request
    )

@router.post("/{id}/members", response_model=ResearchMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    id: int,
    member_data: ResearchMemberCreate,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_member = add_member_to_project(db, id, member_data.user_id, int(current_user.id))
    return success_response(
        data=new_member,
        message="Thêm thành viên thành công",
        request=request,
        status_code=status.HTTP_201_CREATED
    )

@router.delete("/{id}/members/{user_id}", status_code=status.HTTP_200_OK)
def remove_member(
    id: int,
    user_id: int,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    remove_member_from_project(db, id, user_id, int(current_user.id))
    return success_response(
        data=None,
        message="Xóa thành viên thành công",
        request=request
    )

@router.get("/{id}/members", response_model=List[ResearchMemberResponse], status_code=status.HTTP_200_OK)
def get_members(
    id: int,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_project_members(db, id, int(current_user.id))