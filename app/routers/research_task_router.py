from typing import Optional, Literal

from fastapi import APIRouter, Depends, Request, Query, status
from sqlalchemy.orm import Session

from app.schemas.research_tasks import ResearchTaskCreate, ResearchTaskUpdate, ResearchTaskResponse
from app.models.research_tasks import TaskStatus, TaskPriority
from app.models.users import UsersModel
from app.db.database import get_db
from app.dependencies.auth import get_current_user
from app.core.responses import success_response, APIResponse
from app.services.research_task_service import (
    create_research_task,
    get_research_tasks,
    get_research_task_by_id,
    update_research_task,
    delete_research_task,
)


router = APIRouter(tags=["Research Tasks"])


@router.post("/research-projects/{id}/research-tasks", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    id: int,
    task_data: ResearchTaskCreate,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_task = create_research_task(
        db=db,
        project_id=id,
        task_data=task_data,
        current_user_id=current_user.id
    )

    return success_response(
        data=ResearchTaskResponse.model_validate(new_task),
        message="Tạo nhiệm vụ nghiên cứu thành công",
        request=request,
        status_code=status.HTTP_201_CREATED
    )


@router.get("/research-projects/{id}/research-tasks", response_model=APIResponse, status_code=status.HTTP_200_OK)
def list_tasks(
    id: int,
    request: Request,
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority_filter: Optional[TaskPriority] = Query(None, alias="priority"),
    assignee_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Tìm theo title"),
    sort_by: Literal["created_at", "due_date"] = Query("created_at"),
    order: Literal["asc", "desc"] = Query("desc"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tasks, total = get_research_tasks(
        db=db,
        project_id=id,
        current_user_id=current_user.id,
        status_filter=status_filter,
        priority_filter=priority_filter,
        assignee_id=assignee_id,
        search=search,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset
    )

    return success_response(
        data={
            "items": [ResearchTaskResponse.model_validate(t) for t in tasks],
            "total": total,
            "limit": limit,
            "offset": offset
        },
        message="Lấy danh sách nhiệm vụ nghiên cứu thành công",
        request=request
    )


@router.get("/research-tasks/{id}", response_model=APIResponse, status_code=status.HTTP_200_OK)
def get_task_by_id(
    id: int,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_research_task_by_id(
        db=db,
        task_id=id,
        current_user_id=current_user.id
    )

    return success_response(
        data=ResearchTaskResponse.model_validate(task),
        message="Lấy thông tin nhiệm vụ nghiên cứu thành công",
        request=request
    )


@router.patch("/research-tasks/{id}", response_model=APIResponse, status_code=status.HTTP_200_OK)
def update_task(
    id: int,
    task_data: ResearchTaskUpdate,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_task = update_research_task(
        db=db,
        task_id=id,
        task_data=task_data,
        current_user_id=current_user.id
    )

    return success_response(
        data=ResearchTaskResponse.model_validate(updated_task),
        message="Cập nhật nhiệm vụ nghiên cứu thành công",
        request=request
    )


@router.delete("/research-tasks/{id}", response_model=APIResponse, status_code=status.HTTP_200_OK)
def delete_task(
    id: int,
    request: Request,
    current_user: UsersModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delete_research_task(
        db=db,
        task_id=id,
        current_user_id=current_user.id
    )

    return success_response(
        data=None,
        message="Xóa nhiệm vụ nghiên cứu thành công",
        request=request
    )