from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import get_db
from app.db.models import Project
from app.schemas.project import ProjectUpdate
from app.db.crud_user import get_current_user
from pydantic import BaseModel

router = APIRouter()


@router.put("/{project_id}/coords")
async def update_project_coords(
    project_id: int,
    req: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1. Proje var mı?
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Kullanıcıya mı ait?
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")

    # 3. Koordinatları güncelle
    project.pos_x = req.pos_x
    project.pos_y = req.pos_y
    project.width = req.width
    project.height = req.height
    project.radius = req.radius

    await db.commit()
    await db.refresh(project)

    return {
        "message": "Coordinates updated successfully",
        "project": {
            "id": project.id,
            "name": project.name,
            "pos_x": project.pos_x,
            "pos_y": project.pos_y,
            "width": project.width,
            "height": project.height,
            "radius": project.radius
        }
    }
