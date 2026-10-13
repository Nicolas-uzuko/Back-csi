"""Enforce the archive category/type/confidentiality reference in PostgreSQL."""
from typing import Sequence, Union

from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_documents_classification_coherente",
        "documents",
        "(categorie_archive = 'A' AND confidentialite = 'NON_CONFIDENTIEL' AND type_document IN ('CORRESPONDANCE_ARRIVEE_3', 'CAHIER_ENREGISTREMENT_3', 'COPIE_CORRESPONDANCE_2', 'AVIS_MUTATION', 'ORDRE_GENDARMERIE_NATIONALE', 'REGISTRE_PERMISSIONNAIRES')) OR "
        "(categorie_archive = 'B' AND confidentialite = 'CONFIDENTIEL' AND type_document IN ('CORRESPONDANCE_ARRIVEE_3S', 'CAHIER_ENREGISTREMENT_3S', 'COPIE_CORRESPONDANCE_4', 'ARCHIVE_PROCES_VERBAL', 'REGISTRE_PROCES_VERBAUX', 'CAHIER_SERVICE', 'BULLETIN_SERVICE'))",
    )


def downgrade() -> None:
    op.drop_constraint("ck_documents_classification_coherente", "documents", type_="check")
