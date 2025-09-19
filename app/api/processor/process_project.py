from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import get_db
from app.db.models import Project
from app.schemas.project import ProjectUpdate
from app.db.crud_user import get_current_user
from app.api.processor.tasks import process_project_task

router = APIRouter()

@router.post("/{project_id}/process")
async def process_project(
    project_id: int,
    update_data: ProjectUpdate,              # 🔹 frontend’den gelen güncel değerler
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to process this project")

    # 🔹 DB güncelle
    project.pos_x = update_data.pos_x
    project.pos_y = update_data.pos_y
    project.width = update_data.width
    project.height = update_data.height
    project.radius = update_data.radius
    
    await db.commit()
    await db.refresh(project)

    # 🔹 Celery task tetikle
    task = process_project_task.delay(project_id)

    return {
        "message": "Processing started with updated values",
        "task_id": task.id,
        "updated_values": update_data.dict()
    }
