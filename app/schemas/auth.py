from pydantic import BaseModel, EmailStr, Field

from app.schemas.utilisateur import _validate_password
from pydantic import field_validator


class LoginRequest(BaseModel):
    identifiant: str = Field(..., min_length=1, max_length=255)
    mot_de_passe: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str = Field(..., min_length=20, max_length=256)
    nouveau_mot_de_passe: str = Field(..., min_length=8, max_length=128)

    _password = field_validator("nouveau_mot_de_passe")(_validate_password)
