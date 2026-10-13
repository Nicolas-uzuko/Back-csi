import os

import pytest
from httpx import AsyncClient
from sqlalchemy import delete

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.historique_action import HistoriqueAction
from app.models.utilisateur import RoleUtilisateur, StatutUtilisateur, Utilisateur


pytestmark = pytest.mark.asyncio


@pytest.mark.skipif(os.getenv("RUN_POSTGRES_TESTS") != "1", reason="requires a configured local PostgreSQL")
async def test_real_postgres_auth_permissions_and_validation():
    identifiers = {"smoke-admin@example.com", "smoke-user@example.com"}
    async with AsyncSessionLocal() as db:
        await db.execute(delete(HistoriqueAction).where(HistoriqueAction.identifiant_utilisateur.in_(["smoke-admin", "smoke-user"])))
        await db.execute(delete(Utilisateur).where(Utilisateur.email.in_(identifiers)))
        admin = Utilisateur(
            nom="Smoke", nom_utilisateur="smoke-admin", email="smoke-admin@example.com",
            mot_de_passe_hash=hash_password("AdminPass1"), role=RoleUtilisateur.ADMIN, statut=StatutUtilisateur.ACTIF,
        )
        ordinary = Utilisateur(
            nom="Smoke", nom_utilisateur="smoke-user", email="smoke-user@example.com",
            mot_de_passe_hash=hash_password("UserPass1"), role=RoleUtilisateur.UTILISATEUR, statut=StatutUtilisateur.ACTIF,
        )
        db.add_all([admin, ordinary])
        await db.commit()

    try:
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            admin_response = await client.post("/api/v1/auth/login", json={"identifiant": "smoke-admin", "mot_de_passe": "AdminPass1"})
            assert admin_response.status_code == 200
            admin_token = admin_response.json()["access_token"]
            assert (await client.get("/api/v1/plaintes", headers={"Authorization": f"Bearer {admin_token}"})).status_code == 200

            user_response = await client.post("/api/v1/auth/login", json={"identifiant": "smoke-user@example.com", "mot_de_passe": "UserPass1"})
            assert user_response.status_code == 200
            user_token = user_response.json()["access_token"]
            assert (await client.get("/api/v1/plaintes", headers={"Authorization": f"Bearer {user_token}"})).status_code == 403
            assert (await client.post("/api/v1/courriers-arrivee", json={"categorie": "/9", "categorie_archive": "A"}, headers={"Authorization": f"Bearer {admin_token}"})).status_code == 422
    finally:
        async with AsyncSessionLocal() as db:
            await db.execute(delete(HistoriqueAction).where(HistoriqueAction.identifiant_utilisateur.in_(["smoke-admin", "smoke-user"])))
            await db.execute(delete(Utilisateur).where(Utilisateur.email.in_(identifiers)))
            await db.commit()
