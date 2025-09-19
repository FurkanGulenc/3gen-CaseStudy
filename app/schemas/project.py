from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---------------------------
# Project Create Request
# ---------------------------
class ProjectCreate(BaseModel):
    name: str
    feed_url: str


# ---------------------------
# Project Update Request
# ---------------------------
class ProjectUpdate(BaseModel):
    pos_x: Optional[int] = None
    pos_y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    radius: Optional[int] = None


# ---------------------------
# Project Response
# ---------------------------
class ProjectResponse(BaseModel):
    id: int
    name: str
    feed_url: str
    frame_image: str
    pos_x: int
    pos_y: int
    width: int
    height: int
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy objelerini Pydantic'e dönüştürür
