"""Ajouter les champs Message Radio (heure_depart, priorite, indicatif, corps_message) aux courriers."""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── courriers_arrivee ──────────────────────────────────────────────────
    op.add_column("courriers_arrivee", sa.Column("heure_depart", sa.String(20), nullable=True))
    op.add_column("courriers_arrivee", sa.Column("priorite", sa.String(5), nullable=True))
    op.add_column("courriers_arrivee", sa.Column("indicatif", sa.String(100), nullable=True))
    op.add_column("courriers_arrivee", sa.Column("corps_message", sa.Text(), nullable=True))

    # ── courriers_depart ───────────────────────────────────────────────────
    op.add_column("courriers_depart", sa.Column("heure_depart", sa.String(20), nullable=True))
    op.add_column("courriers_depart", sa.Column("priorite", sa.String(5), nullable=True))
    op.add_column("courriers_depart", sa.Column("indicatif", sa.String(100), nullable=True))
    op.add_column("courriers_depart", sa.Column("corps_message", sa.Text(), nullable=True))


def downgrade() -> None:
    # ── courriers_depart ───────────────────────────────────────────────────
    op.drop_column("courriers_depart", "corps_message")
    op.drop_column("courriers_depart", "indicatif")
    op.drop_column("courriers_depart", "priorite")
    op.drop_column("courriers_depart", "heure_depart")

    # ── courriers_arrivee ──────────────────────────────────────────────────
    op.drop_column("courriers_arrivee", "corps_message")
    op.drop_column("courriers_arrivee", "indicatif")
    op.drop_column("courriers_arrivee", "priorite")
    op.drop_column("courriers_arrivee", "heure_depart")