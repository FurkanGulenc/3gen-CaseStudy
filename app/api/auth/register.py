from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.auth import RegisterRequest
from app.services.auth.register_service import register_service

router = APIRouter()

@router.post(
    "/register",
    summary="Register Endpoint",
    description="Yeni kullanıcı kaydı oluşturur.",
    responses={
        200: {"description": "The user has been successfully registered."},
        400: {"description": "The username or email is already registered."},
        422: {"description": "Validation error. Ensure all required fields are provided and valid."}
    }
)
async def register(
    req: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await register_service(req=req, db=db)
        return user
    except HTTPException as e:
        # service içinde fırlatılan HTTPException doğrudan client'a gider
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
