from fastapi import APIRouter, Depends
from app.db.crud_user import get_current_user
from app.db.models import User

router = APIRouter()

@router.get("/auth/me")
async def get_me(current_user:User=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }
