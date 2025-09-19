from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

# ----------------------
# 1. Users
# ----------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(64), nullable=True)   # opsiyonel, verify_password buna göre çalışıyor mu bak
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="owner")
    refresh_tokens = relationship("RefreshToken", back_populates="user")


# ----------------------
# 2. Projects
# ----------------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String(100), nullable=False, index=True)
    feed_url = Column(Text, nullable=False)
    frame_image = Column(String(255), nullable=False)   # dosya yolu
    pos_x = Column(Integer, default=0)
    pos_y = Column(Integer, default=0)
    width = Column(Integer, default=0)
    height = Column(Integer, default=0)
    radius = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    outputs = relationship("OutputImage", back_populates="project")


# ----------------------
# 3. OutputImages
# ----------------------
class OutputImage(Base):
    __tablename__ = "output_images"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    product_id = Column(String(100), index=True)               # XML <id>
    source_image_url = Column(Text, nullable=False)            # XML <image_link>
    output_path = Column(String(255), nullable=False)          # media/outputs/...
    status = Column(String(20), default="PENDING")             # PENDING/SUCCESS/FAILED
    rendered_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="outputs")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    token = Column(Text, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")
