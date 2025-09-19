from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.db.models import User, RefreshToken
from app.db.base import get_db
from app.core.config import SECRET_KEY, ALGORITHM
from typing import Optional

# Swagger UI’daki authorize için
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ---------------------------
# Create user
# ---------------------------
async def create_user(db: AsyncSession, username: str, email: str, password_hash: str, salt: Optional[str] = None):
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        salt=salt,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ---------------------------
# Delete user
# ---------------------------
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # refresh tokenları sil
        await db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
        # user sil
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


# ---------------------------
# Get user by email
# ---------------------------
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


# ---------------------------
# Get user by username
# ---------------------------
async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


# ---------------------------
# Get current user (from JWT)
# ---------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            raise credentials_exception
        return user

    except JWTError:
        raise credentials_exception


# ---------------------------
# Update user
# ---------------------------
async def update_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    username: Optional[str] = None,
    email: Optional[str] = None
):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        update_data = {}
        if username is not None:
            update_data["username"] = username
        if email is not None:
            update_data["email"] = email

        if update_data:
            await db.execute(update(User).where(User.id == user_id).values(**update_data))
            await db.commit()

        result = await db.execute(select(User).where(User.id == user_id))
        updated_user = result.scalars().first()
        return {"message": "User updated successfully", "user": updated_user}

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )
