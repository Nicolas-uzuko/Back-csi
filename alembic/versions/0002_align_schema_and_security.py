"""Align the initial register schema with the validated data model.

This revision removes the previously introduced non-business ``entete_message``
columns, adds PostgreSQL identity generation for all BIGINT keys, and enforces
the common archive metadata invariants.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE_KEYS = {
    "utilisateurs": "id",
    "courriers_arrivee": "id_courrier",
    "courriers_depart": "id_courrier",
    "plaintes": "id_plainte",
    "proces_verbaux": "id_pv",
    "services_courants": "id_service",
    "situations_prise_arme": "id_situation",
    "documents": "id_document",
    "historique_actions": "id_historique",
}


def upgrade() -> None:
    for table in ("courriers_arrivee", "courriers_depart"):
        op.drop_column(table, "entete_message")

    op.alter_column("documents", "taille_octets", existing_type=sa.Integer(), type_=sa.BigInteger())
    op.create_index("ix_documents_categorie_archive", "documents", ["categorie_archive"])
    op.create_check_constraint(
        "ck_documents_source_coherente",
        "documents",
        "(table_source IS NULL AND id_source IS NULL) OR "
        "(table_source IN ('courriers_arrivee', 'courriers_depart', 'plaintes', 'proces_verbaux', 'services_courants', 'situations_prise_arme') AND id_source IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_documents_type_document_autorise",
        "documents",
        "type_document IN ('CORRESPONDANCE_ARRIVEE_3', 'CAHIER_ENREGISTREMENT_3', 'COPIE_CORRESPONDANCE_2', 'AVIS_MUTATION', 'ORDRE_GENDARMERIE_NATIONALE', 'REGISTRE_PERMISSIONNAIRES', 'CORRESPONDANCE_ARRIVEE_3S', 'CAHIER_ENREGISTREMENT_3S', 'COPIE_CORRESPONDANCE_4', 'ARCHIVE_PROCES_VERBAL', 'REGISTRE_PROCES_VERBAUX', 'CAHIER_SERVICE', 'BULLETIN_SERVICE')",
    )
    op.create_check_constraint(
        "ck_documents_conservation_coherente",
        "documents",
        "(mode_conservation = 'PHYSIQUE' AND emplacement_physique IS NOT NULL) OR "
        "(mode_conservation IN ('NUMERIQUE', 'MIXTE') AND nom_interne IS NOT NULL AND chemin_stockage IS NOT NULL)",
    )
    op.create_check_constraint("ck_documents_taille_positive", "documents", "taille_octets IS NULL OR taille_octets >= 0")
    op.create_check_constraint("ck_documents_sha256_format", "documents", "sha256 IS NULL OR sha256 ~ '^[0-9a-fA-F]{64}$'")

    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_utilisateurs_date_modification()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.date_modification = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_utilisateurs_date_modification
        BEFORE UPDATE ON utilisateurs
        FOR EACH ROW EXECUTE FUNCTION set_utilisateurs_date_modification();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_utilisateurs_date_modification ON utilisateurs")
    op.execute("DROP FUNCTION IF EXISTS set_utilisateurs_date_modification()")
    for constraint in (
        "ck_documents_sha256_format",
        "ck_documents_taille_positive",
        "ck_documents_conservation_coherente",
        "ck_documents_type_document_autorise",
        "ck_documents_source_coherente",
    ):
        op.drop_constraint(constraint, "documents", type_="check")
    op.drop_index("ix_documents_categorie_archive", table_name="documents")
    op.alter_column("documents", "taille_octets", existing_type=sa.BigInteger(), type_=sa.Integer())
    op.add_column("courriers_depart", sa.Column("entete_message", sa.String(100), nullable=True))
    op.add_column("courriers_arrivee", sa.Column("entete_message", sa.String(100), nullable=True))
