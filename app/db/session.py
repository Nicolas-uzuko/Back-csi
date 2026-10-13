from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_admin() -> None:
    """Initialise le premier utilisateur Administrateur s'il n'existe pas encore."""
    import logging
    from sqlalchemy import select, or_
    from app.models.utilisateur import Utilisateur, RoleUtilisateur, StatutUtilisateur
    from app.core.security import hash_password

    logger = logging.getLogger("csi.init_admin")
    
    async with AsyncSessionLocal() as session:
        try:
            admin_email = settings.first_admin_email.strip().lower()
            admin_username = settings.first_admin_username.strip()

            stmt = select(Utilisateur).where(
                or_(
                    Utilisateur.email == admin_email,
                    Utilisateur.nom_utilisateur == admin_username,
                )
            )
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if existing_user is None:
                new_admin = Utilisateur(
                    nom=settings.first_admin_nom,
                    prenom=settings.first_admin_prenom,
                    matricule=settings.first_admin_matricule,
                    nom_utilisateur=admin_username,
                    email=admin_email,
                    mot_de_passe_hash=hash_password(settings.first_admin_password),
                    role=RoleUtilisateur.ADMIN,
                    statut=StatutUtilisateur.ACTIF,
                )
                session.add(new_admin)
                await session.commit()
                logger.info(f"Administrateur initial créé avec succès ({admin_email}).")
            else:
                # S'assurer qu'il a le rôle ADMIN et est ACTIF
                if existing_user.role != RoleUtilisateur.ADMIN or existing_user.statut != StatutUtilisateur.ACTIF:
                    existing_user.role = RoleUtilisateur.ADMIN
                    existing_user.statut = StatutUtilisateur.ACTIF
                    await session.commit()
                    logger.info(f"Utilisateur existant {admin_email} promu en ADMIN ACTIF.")
        except Exception as e:
            await session.rollback()
            logger.warning(f"Impossible d'initialiser l'admin au démarrage (base de données non disponible ou non migrée) : {e}")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

