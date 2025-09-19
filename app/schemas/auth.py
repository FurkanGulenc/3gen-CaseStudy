from pydantic import BaseModel, EmailStr
from datetime import datetime

# ---------------------------
# Register için request body
# ---------------------------
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

# ---------------------------
# Login / Token response
# ---------------------------
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

