from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.utilisateur import Utilisateur
from app.repositories.base import AsyncRepository


class UtilisateurRepository(AsyncRepository[Utilisateur]):
    model = Utilisateur
    id_field = "id"

    async def by_login(self, identifiant: str) -> Optional[Utilisateur]:
        return await self.db.scalar(
            select(Utilisateur).where(
                or_(Utilisateur.email == identifiant.lower(), Utilisateur.nom_utilisateur == identifiant)
            )
        )

    async def by_email(self, email: str) -> Optional[Utilisateur]:
        return await self.db.scalar(select(Utilisateur).where(Utilisateur.email == email.lower()))
