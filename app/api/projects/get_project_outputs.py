from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import get_db
from app.db.models import Project, OutputImage
from app.db.crud_user import get_current_user

router = APIRouter()

@router.get("/projects/{project_id}/outputs")
async def get_project_outputs(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # Proje var mı?
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Kullanıcıya mı ait?
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Output görsellerini çek
    result = await db.execute(
        select(OutputImage).where(OutputImage.project_id == project.id)
    )
    outputs = result.scalars().all()

    return [
        {
            "id": o.id,
            "product_id": o.product_id,
            "image_path": o.output_path,
            "created_at": o.rendered_at,
        }
        for o in outputs
    ]
