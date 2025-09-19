from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import User
from app.utils.password_utils import hash_password
from app.schemas.auth import RegisterRequest

async def register_service(req: RegisterRequest, db: AsyncSession):
    result = await db.execute(
        select(User).where((User.email == req.email) | (User.username == req.username))
    )
    db_user = result.scalars().first()
    if db_user:
        if db_user.email == req.email:
            raise HTTPException(status_code=400, detail="E-mail address already registered")
        if db_user.username == req.username:
            raise HTTPException(status_code=400, detail="Username already registered")

    # utils’ten hash çağrısı
    hashed_pw, salt = hash_password(req.password)

    new_user = User(
        username=req.username,
        email=req.email,
        password_hash=hashed_pw,
        salt=salt
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
