from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.schemas.research_projects import ResearchProjectCreate, ResearchProjectUpdate
from app.models.research_projects import ResearchProjectsModel
from app.models.research_members import ResearchMembersModel, MemberRole


def create_research_project(db: Session, project_data: ResearchProjectCreate, owner_id: int):
    # Khởi tạo đề tài nghiên cứu
    new_research_project = ResearchProjectsModel(
        name=project_data.name,
        description=project_data.description,
        owner_id=owner_id
    )
    db.add(new_research_project)
    db.flush() # Đẩy xuống DB lấy ID nhưng chưa commit
    
    # Gán người tạo vào bảng thành viên với role OWNER
    new_member = ResearchMembersModel(
        project_id=new_research_project.id,
        user_id=owner_id,
        role=MemberRole.OWNER
    )
    db.add(new_member)
    
    db.commit()
    db.refresh(new_research_project)
    return new_research_project

def get_research_projects(db: Session, user_id: int, search_name: str | None):
    query = db.query(ResearchProjectsModel).outerjoin(
        ResearchMembersModel, ResearchProjectsModel.id == ResearchMembersModel.project_id
    ).filter(
        or_(
            ResearchProjectsModel.owner_id == user_id,
            ResearchMembersModel.user_id == user_id
        )
    )
    if search_name:
        query = query.filter(ResearchProjectsModel.name.ilike(f"%{search_name}%"))
    return query.all()

def get_research_project_by_id(db: Session, project_id: int, user_id: int):
    project = db.query(ResearchProjectsModel).filter(ResearchProjectsModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Đề tài nghiên cứu không tồn tại")
    
    # Kiểm tra BOLA: Chỉ owner hoặc member mới được xem
    is_owner = project.owner_id == user_id
    is_member = db.query(ResearchMembersModel).filter(
        ResearchMembersModel.project_id == project_id,
        ResearchMembersModel.user_id == user_id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ thành viên đề tài nghiên cứu mới được xem")
        
    return project

def update_research_project(db: Session, project_id: int, project_data: ResearchProjectUpdate, owner_id: int):
    project = db.query(ResearchProjectsModel).filter(ResearchProjectsModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Đề tài nghiên cứu không tồn tại")
        
    if project.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ OWNER được sửa đề tài nghiên cứu")
        
    if project_data.name is not None:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
        
    db.commit()
    db.refresh(project)
    return project

def delete_research_project(db: Session, project_id: int, owner_id: int):
    project = db.query(ResearchProjectsModel).filter(ResearchProjectsModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Đề tài nghiên cứu không tồn tại")
        
    if project.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ OWNER được xóa đề tài nghiên cứu")
        
    db.delete(project)
    db.commit()
    return True

def add_member_to_project(db: Session, project_id: int, new_user_id: int, owner_id: int):
    project = db.query(ResearchProjectsModel).filter(ResearchProjectsModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Đề tài nghiên cứu không tồn tại")
        
    if project.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ OWNER được thêm thành viên")
        
    # Chặn thêm trùng
    existing_member = db.query(ResearchMembersModel).filter(
        ResearchMembersModel.project_id == project_id,
        ResearchMembersModel.user_id == new_user_id
    ).first()
    
    if existing_member or project.owner_id == new_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User đã là thành viên của đề tài nghiên cứu")
        
    new_member = ResearchMembersModel(
        project_id=project_id,
        user_id=new_user_id,
        role=MemberRole.MEMBER
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

def remove_member_from_project(db: Session, project_id: int, remove_user_id: int, owner_id: int):
    project = db.query(ResearchProjectsModel).filter(ResearchProjectsModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Đề tài nghiên cứu không tồn tại")
        
    if project.owner_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ OWNER được xóa thành viên")
        
    # Chặn xóa owner cuối cùng
    if project.owner_id == remove_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không được xóa owner cuối cùng")
        
    member = db.query(ResearchMembersModel).filter(
        ResearchMembersModel.project_id == project_id,
        ResearchMembersModel.user_id == remove_user_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thành viên không tồn tại trong đề tài nghiên cứu")
        
    db.delete(member)
    db.commit()
    return True

def get_project_members(db: Session, project_id: int, current_user_id: int):
    project = db.query(ResearchProjectsModel).filter(ResearchProjectsModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Đề tài nghiên cứu không tồn tại")
        
    is_owner = project.owner_id == current_user_id
    is_member = db.query(ResearchMembersModel).filter(
        ResearchMembersModel.project_id == project_id,
        ResearchMembersModel.user_id == current_user_id
    ).first()
    
    if not is_owner and not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chỉ thành viên đề tài nghiên cứu mới được xem danh sách")
        
    return db.query(ResearchMembersModel).filter(ResearchMembersModel.project_id == project_id).all()