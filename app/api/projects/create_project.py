from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.db.models import Project, User
from app.db.crud_user import get_current_user
import os, shutil
from datetime import datetime
from app.schemas.project import ProjectResponse

router = APIRouter()

@router.post("/create", response_model=ProjectResponse)
async def create_project(
    name: str = Form(...),
    feed_url: str = Form(...),
    frame_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("📥 DEBUG name:", name)
    print("📥 DEBUG feed_url:", feed_url)
    print("📥 DEBUG frame_image:", frame_image.filename if frame_image else None)
    
    # frame'i media/frames içine kaydet
    frames_dir = "media/frames"
    os.makedirs(frames_dir, exist_ok=True)

    file_path = os.path.join(frames_dir, frame_image.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(frame_image.file, buffer)

    new_project = Project(
        user_id=current_user.id,
        name=name,
        feed_url=feed_url,
        frame_image=file_path,
        pos_x=0, pos_y=0, width=0, height=0,
        created_at=datetime.utcnow()
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return new_project
