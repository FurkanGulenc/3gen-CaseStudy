from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta

from app.db.base import get_db
from app.db.models import User, RefreshToken
from app.schemas.auth import TokenResponse
from app.utils.password_utils import verify_password
from app.utils.jwt_handler import create_access_token, create_refresh_token  # senin mevcut util’in

router = APIRouter()

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login Endpoint",
    description="Kullanıcı email veya username ile giriş yapar."
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # username alanına email gelecek
    
    result = await db.execute(
    select(User).where((User.email == form_data.username) | (User.username == form_data.username))
)
    print("Form username:", form_data.username)
    print("Form password:", form_data.password)

    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(form_data.password, user.password_hash, user.salt):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # eski refresh token’ları temizle
    result = await db.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))
    db_refresh_tokens = result.scalars().all()
    for db_refresh_token in db_refresh_tokens:
        await db.delete(db_refresh_token)

    # yeni refresh token
    refresh_token = create_refresh_token(data={"sub": user.email})
    new_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=4),
    )
    db.add(new_refresh_token)

    # yeni access token
    access_token = create_access_token(data={"sub": user.email})

    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
