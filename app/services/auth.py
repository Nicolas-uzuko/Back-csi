from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_reset_token,
    hash_password,
    hash_reset_token,
    verify_password,
)
from app.models.utilisateur import StatutUtilisateur, Utilisateur
from app.repositories.utilisateur import UtilisateurRepository
from app.schemas.auth import LoginRequest, ResetPasswordConfirm
from app.services.audit import audit_service
from app.services.email import send_password_reset_email


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UtilisateurRepository(db)

    async def login(self, data: LoginRequest, ip_address: Optional[str] = None) -> Tuple[str, str]:
        user = await self.repository.by_login(data.identifiant)
        if user is None or user.statut != StatutUtilisateur.ACTIF or not verify_password(data.mot_de_passe, user.mot_de_passe_hash):
            await audit_service.log(
                self.db, action="CONNEXION", identifier=data.identifiant[:100],
                details={"motif": "identifiants_invalides"}, ip_address=ip_address,
                success=False, independent_commit=True,
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
        access = create_access_token(
            user.id,
            {
                "role": user.role.value,
                "email": user.email,
                "nom_utilisateur": user.nom_utilisateur,
                "nom": user.nom,
                "prenom": user.prenom,
                "matricule": user.matricule,
            },
        )
        refresh = create_refresh_token(user.id)
        await audit_service.log(
            self.db, action="CONNEXION", user_id=user.id, identifier=user.nom_utilisateur,
            ip_address=ip_address, success=True,
        )
        return access, refresh

    async def refresh(self, token: str, ip_address: Optional[str] = None) -> Tuple[str, str]:
        try:
            payload = decode_token(token)
            if payload.get("type") != "refresh":
                raise ValueError
            user_id = int(payload["sub"])
        except (JWTError, ValueError, TypeError, KeyError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalide")
        user = await self.repository.get(user_id)
        if user is None or user.statut != StatutUtilisateur.ACTIF:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalide")
        await audit_service.log(self.db, action="RENOUVELLEMENT_TOKEN", user_id=user.id, identifier=user.nom_utilisateur, ip_address=ip_address, success=True)
        return create_access_token(
            user.id,
            {
                "role": user.role.value,
                "email": user.email,
                "nom_utilisateur": user.nom_utilisateur,
                "nom": user.nom,
                "prenom": user.prenom,
                "matricule": user.matricule,
            },
        ), create_refresh_token(user.id)

    async def request_password_reset(self, email: str, ip_address: Optional[str] = None) -> None:
        user = await self.repository.by_email(email)
        if user is not None and user.statut == StatutUtilisateur.ACTIF:
            plain_token, hashed_token = generate_reset_token()
            user.reset_token_hash = hashed_token
            user.reset_token_expire = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(minutes=settings.reset_token_expire_minutes)
            await self.db.flush()
            await send_password_reset_email(user.email, plain_token)
            await audit_service.log(self.db, action="DEMANDE_RESET_MOT_DE_PASSE", user_id=user.id, identifier=user.nom_utilisateur, ip_address=ip_address, success=True)
        else:
            await audit_service.log(self.db, action="DEMANDE_RESET_MOT_DE_PASSE", identifier=email[:100], ip_address=ip_address, success=True, details={"resultat": "non_divulgation"}, independent_commit=True)

    async def confirm_password_reset(self, data: ResetPasswordConfirm, ip_address: Optional[str] = None) -> None:
        token_hash = hash_reset_token(data.token)
        now = datetime.now(timezone.utc)
        user = await self.db.scalar(select(Utilisateur).where(and_(Utilisateur.reset_token_hash == token_hash, Utilisateur.reset_token_expire > now)))
        if user is None or user.reset_token_hash is None or not user.reset_token_expire or user.reset_token_expire <= now:
            await audit_service.log(self.db, action="RESET_MOT_DE_PASSE", ip_address=ip_address, success=False, independent_commit=True)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Jeton de réinitialisation invalide ou expiré")
        user.mot_de_passe_hash = hash_password(data.nouveau_mot_de_passe)
        user.reset_token_hash = None
        user.reset_token_expire = None
        await audit_service.log(self.db, action="RESET_MOT_DE_PASSE", user_id=user.id, identifier=user.nom_utilisateur, ip_address=ip_address, success=True)


def password_hash_for_create(password: str) -> str:
    return hash_password(password)
