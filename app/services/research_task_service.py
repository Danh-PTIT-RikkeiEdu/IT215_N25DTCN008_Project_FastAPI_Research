from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from fastapi import HTTPException, status

from app.schemas.research_tasks import ResearchTaskCreate, ResearchTaskUpdate
from app.models.research_tasks import ResearchTasksModel, TaskStatus, TaskPriority
from app.models.research_projects import ResearchProjectsModel
from app.models.research_members import ResearchMembersModel


def get_project_or_404(db: Session, project_id: int) -> ResearchProjectsModel:
    project = db.query(ResearchProjectsModel).filter(ResearchProjectsModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Đề tài nghiên cứu không tồn tại")
    return project


def is_project_member(db: Session, project: ResearchProjectsModel, user_id: int) -> bool:
    if project.owner_id == user_id:
        return True
    member = db.query(ResearchMembersModel).filter(
        ResearchMembersModel.project_id == project.id,
        ResearchMembersModel.user_id == user_id
    ).first()
    return member is not None


def create_research_task(db: Session, project_id: int, task_data: ResearchTaskCreate, current_user_id: int):
    project = get_project_or_404(db, project_id)

    # Chỉ thành viên (owner hoặc member) của đề tài mới được tạo nhiệm vụ
    if not is_project_member(db, project, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ thành viên đề tài nghiên cứu mới được tạo nhiệm vụ"
        )

    # Chọn ng làm thì ng đó phải là ng trong dự án
    if task_data.assignee_id is not None:
        if not is_project_member(db, project, task_data.assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee phải là thành viên của đề tài nghiên cứu"
            )

    new_task = ResearchTasksModel(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        project_id=project_id,           
        assignee_id=task_data.assignee_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_research_tasks(
    db: Session,
    project_id: int,
    current_user_id: int,
    status_filter: Optional[TaskStatus] = None,
    priority_filter: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    limit: int = 10,
    offset: int = 0,
):
    project = get_project_or_404(db, project_id)

    # Chỉ thành viên đề tài mới được xem danh sách nhiệm vụ của đề tài đó
    if not is_project_member(db, project, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ thành viên đề tài nghiên cứu mới được xem nhiệm vụ"
        )

    query = db.query(ResearchTasksModel).filter(ResearchTasksModel.project_id == project_id)

    if status_filter is not None:
        query = query.filter(ResearchTasksModel.status == status_filter)
    if priority_filter is not None:
        query = query.filter(ResearchTasksModel.priority == priority_filter)
    if assignee_id is not None:
        query = query.filter(ResearchTasksModel.assignee_id == assignee_id)
    if search:
        query = query.filter(ResearchTasksModel.title.ilike(f"%{search}%"))

    total = query.count() # Đếm tổng số bản ghi đã tìm được

    # Sắp xếp theo ngày tạo nhiệm vụ hoặc theo ngày đến hạn nhiệm vụ (deadline)
    sort_column = ResearchTasksModel.due_date if sort_by == "due_date" else ResearchTasksModel.created_at

    # Mặc định là giảm dần (desc), Nếu truyền asc thì tăng dần dựa trên sort_column
    order_func = asc if order == "asc" else desc

    # qua bên db là ORDER BY cột và dạng sắp xếp
    query = query.order_by(order_func(sort_column))

    # offset(offset) bỏ qua n bảo ghi đầu
    # limit(limit) lấy tối đa n bản ghi trong 1 trang 
    tasks = query.offset(offset).limit(limit).all()

    # trả tuple, dựa vào tasks trả ndung và total tạo phân trang 
    return tasks, total


def get_research_task_by_id(db: Session, task_id: int, current_user_id: int):
    task = db.query(ResearchTasksModel).filter(ResearchTasksModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nhiệm vụ nghiên cứu không tồn tại")

    project = get_project_or_404(db, int(task.project_id))

    # Kiểm tra user có thuộc đề tài nghiên cứu chứa nhiệm vụ này không trước khi trả dữ liệu
    if not is_project_member(db, project, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ thành viên đề tài nghiên cứu mới được xem nhiệm vụ"
        )

    return task


def update_research_task(db: Session, task_id: int, task_data: ResearchTaskUpdate, current_user_id: int):
    task = db.query(ResearchTasksModel).filter(ResearchTasksModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nhiệm vụ nghiên cứu không tồn tại")

    project = get_project_or_404(db, int(task.project_id))

    is_owner = project.owner_id == current_user_id
    is_assignee = task.assignee_id == current_user_id

    if not is_owner and not is_assignee:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền cập nhật nhiệm vụ này")

    # Ng làm nv chỉ đc cập nhật trạng thái
    if not is_owner:
        if (
            task_data.title is not None
            or task_data.description is not None
            or task_data.priority is not None
            or task_data.due_date is not None
            or task_data.assignee_id is not None
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assignee chỉ được phép cập nhật trạng thái (status) của nhiệm vụ"
            )

    # Nếu owner đổi assignee, assignee mới phải là thành viên của đề tài
    if task_data.assignee_id is not None:
        if not is_project_member(db, project, task_data.assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee phải là thành viên của đề tài nghiên cứu"
            )

    # Chỉ cập nhật trường nào có gửi giá trị lên, không đụng tới trường không gửi
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.status is not None:
        task.status = task_data.status
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    if task_data.assignee_id is not None:
        task.assignee_id = task_data.assignee_id

    db.commit()
    db.refresh(task)
    return task


def delete_research_task(db: Session, task_id: int, current_user_id: int):
    task = db.query(ResearchTasksModel).filter(ResearchTasksModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nhiệm vụ nghiên cứu không tồn tại")

    project = get_project_or_404(db, int(task.project_id))

    # Chỉ OWNER của đề tài mới được xóa nhiệm vụ nghiên cứu
    if project.owner_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ OWNER được xóa nhiệm vụ nghiên cứu")

    db.delete(task)
    db.commit()
    return True