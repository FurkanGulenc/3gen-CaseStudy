from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.base import get_db
from app.db.models import Project
from app.db.crud_user import get_current_user

router = APIRouter()

@router.get("/get-projects")
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "created_at": p.created_at,
            "frame_image": p.frame_image,
            "feed_url": p.feed_url
        }
        for p in projects
    ]
