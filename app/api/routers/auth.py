from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, ResetPasswordConfirm, ResetPasswordRequest, TokenResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentification"])


def request_ip(request: Request) -> Optional[str]:
    return request.client.host if request.client else None


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    access, refresh = await AuthService(db).login(data, request_ip(request))
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, request: Request, db: AsyncSession = Depends(get_db)):
    access, refresh_token = await AuthService(db).refresh(data.refresh_token, request_ip(request))
    return TokenResponse(access_token=access, refresh_token=refresh_token)


@router.post("/password-reset/request", status_code=202)
async def request_reset(data: ResetPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)):
    await AuthService(db).request_password_reset(str(data.email), request_ip(request))
    return {"message": "Si le compte existe, un e-mail de réinitialisation a été envoyé."}


@router.post("/password-reset/confirm", status_code=204)
async def confirm_reset(data: ResetPasswordConfirm, request: Request, db: AsyncSession = Depends(get_db)):
    await AuthService(db).confirm_password_reset(data, request_ip(request))
