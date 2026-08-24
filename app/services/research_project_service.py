from sqlalchemy.orm import Session

from app.schemas.research_projects import ResearchProjectCreate
from app.models.research_projects import ResearchProjectsModel


def create_research_project(db: Session, project_data: ResearchProjectCreate, owner_id: int):
    new_research_project = ResearchProjectsModel(
        name = project_data.name,
        description = project_data.description,
        owner_id = owner_id
    )

    db.add(new_research_project)
    db.commit()
    db.refresh(new_research_project)

    return new_research_project

    