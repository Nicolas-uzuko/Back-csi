from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Permission, has_permission
from app.core.security import decode_token, token_type_is
from app.db.session import get_db
from app.models.utilisateur import StatutUtilisateur, Utilisateur


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Utilisateur:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification requise",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if not token_type_is(payload, "access"):
            raise credentials_error
        user_id = int(payload["sub"])
    except (JWTError, ValueError, TypeError, KeyError):
        raise credentials_error

    user = await db.scalar(select(Utilisateur).where(Utilisateur.id == user_id))
    if user is None or user.statut != StatutUtilisateur.ACTIF:
        raise credentials_error
    return user


def require_permission(permission: Permission) -> Callable:
    async def dependency(user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
        if not has_permission(user, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission insuffisante")
        return user

    return dependency
