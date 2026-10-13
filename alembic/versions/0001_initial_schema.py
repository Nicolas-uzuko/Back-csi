"""Initial schema

Revision ID: 0001
Revises: 
Create Date: 2026-10-13
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums
    role_enum = postgresql.ENUM('ADMIN', 'UTILISATEUR', name='role_utilisateur_enum', create_type=False)
    statut_enum = postgresql.ENUM('ACTIF', 'DESACTIVE', name='statut_utilisateur_enum', create_type=False)
    categorie_archive_enum = postgresql.ENUM('A', 'B', name='categorie_archive_enum', create_type=False)
    confidentialite_enum = postgresql.ENUM('NON_CONFIDENTIEL', 'CONFIDENTIEL', name='type_confidentialite_enum', create_type=False)
    mode_conservation_enum = postgresql.ENUM('PHYSIQUE', 'NUMERIQUE', 'MIXTE', name='mode_conservation_enum', create_type=False)
    
    role_enum.create(op.get_bind(), checkfirst=True)
    statut_enum.create(op.get_bind(), checkfirst=True)
    categorie_archive_enum.create(op.get_bind(), checkfirst=True)
    confidentialite_enum.create(op.get_bind(), checkfirst=True)
    mode_conservation_enum.create(op.get_bind(), checkfirst=True)

    # TABLE: utilisateurs
    op.create_table(
        'utilisateurs',
        sa.Column('id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('nom', sa.String(100), nullable=False),
        sa.Column('prenom', sa.String(100), nullable=True),
        sa.Column('matricule', sa.String(50), nullable=True),
        sa.Column('nom_utilisateur', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('telephone', sa.String(10), nullable=True),
        sa.Column('mot_de_passe_hash', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('ADMIN', 'UTILISATEUR', name='role_utilisateur_enum', create_type=False), nullable=False),
        sa.Column('statut', postgresql.ENUM('ACTIF', 'DESACTIVE', name='statut_utilisateur_enum', create_type=False), nullable=False, server_default='ACTIF'),
        sa.Column('date_creation', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('date_modification', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('reset_token_hash', sa.String(64), nullable=True),
        sa.Column('reset_token_expire', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint("telephone ~ '^[0-9]{10}$' OR telephone IS NULL", name='ck_utilisateurs_telephone_format'),
        sa.PrimaryKeyConstraint('id', name='pk_utilisateurs'),
        sa.UniqueConstraint('email', name='uq_utilisateurs_email'),
        sa.UniqueConstraint('nom_utilisateur', name='uq_utilisateurs_nom_utilisateur'),
        sa.UniqueConstraint('matricule', name='uq_utilisateurs_matricule'),
    )
    op.create_index('ix_utilisateurs_email', 'utilisateurs', ['email'])
    op.create_index('ix_utilisateurs_nom_utilisateur', 'utilisateurs', ['nom_utilisateur'])
    op.create_index('ix_utilisateurs_matricule', 'utilisateurs', ['matricule'])

    # TABLE: courriers_arrivee
    op.create_table(
        'courriers_arrivee',
        sa.Column('id_courrier', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('categorie', sa.String(10), nullable=False),
        sa.Column('categorie_archive', sa.CHAR(1), nullable=False),
        sa.Column('entete_message', sa.String(100), nullable=True),
        sa.Column('fm', sa.String(255), nullable=True),
        sa.Column('to', sa.String(255), nullable=True),
        sa.Column('info', sa.Text(), nullable=True),
        sa.Column('numero_ordre', sa.String(50), nullable=True),
        sa.Column('numero_piece', sa.String(100), nullable=True),
        sa.Column('date_piece', sa.Date(), nullable=True),
        sa.Column('date_reception', sa.Date(), nullable=True),
        sa.Column('origine_piece', sa.String(255), nullable=True),
        sa.Column('analyse', sa.Text(), nullable=True),
        sa.Column('observation', sa.Text(), nullable=True),
        sa.CheckConstraint("categorie IN ('/3', '/3S')", name='ck_courriers_arrivee_categorie'),
        sa.CheckConstraint("categorie_archive IN ('A', 'B')", name='ck_courriers_arrivee_categorie_archive'),
        sa.PrimaryKeyConstraint('id_courrier', name='pk_courriers_arrivee'),
    )
    op.create_index('ix_courriers_arrivee_date_reception', 'courriers_arrivee', ['date_reception'])
    op.create_index('ix_courriers_arrivee_categorie', 'courriers_arrivee', ['categorie'])
    op.create_index('ix_courriers_arrivee_numero_ordre', 'courriers_arrivee', ['numero_ordre'])

    # TABLE: courriers_depart
    op.create_table(
        'courriers_depart',
        sa.Column('id_courrier', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('categorie', sa.String(10), nullable=False),
        sa.Column('categorie_archive', sa.CHAR(1), nullable=False),
        sa.Column('entete_message', sa.String(100), nullable=True),
        sa.Column('fm', sa.String(255), nullable=True),
        sa.Column('to', sa.String(255), nullable=True),
        sa.Column('info', sa.Text(), nullable=True),
        sa.Column('reference_message', sa.String(100), nullable=True),
        sa.Column('objet', sa.String(500), nullable=True),
        sa.Column('date_piece', sa.Date(), nullable=True),
        sa.Column('ref', sa.String(100), nullable=True),
        sa.Column('observation', sa.Text(), nullable=True),
        sa.Column('signataire', sa.String(255), nullable=True),
        sa.Column('date_envoi', sa.Date(), nullable=True),
        sa.CheckConstraint("categorie IN ('/2', '/4')", name='ck_courriers_depart_categorie'),
        sa.CheckConstraint("categorie_archive IN ('A', 'B')", name='ck_courriers_depart_categorie_archive'),
        sa.PrimaryKeyConstraint('id_courrier', name='pk_courriers_depart'),
    )
    op.create_index('ix_courriers_depart_date_envoi', 'courriers_depart', ['date_envoi'])
    op.create_index('ix_courriers_depart_categorie', 'courriers_depart', ['categorie'])
    op.create_index('ix_courriers_depart_reference_message', 'courriers_depart', ['reference_message'])

    # TABLE: plaintes
    op.create_table(
        'plaintes',
        sa.Column('id_plainte', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('numero_ordre', sa.String(50), nullable=True),
        sa.Column('nom_plaignant', sa.String(255), nullable=True),
        sa.Column('nom_personne_en_cause', sa.String(255), nullable=True),
        sa.Column('motif_plainte', sa.Text(), nullable=True),
        sa.Column('lieu_acte', sa.String(255), nullable=True),
        sa.Column('telephone_plaignant', sa.String(30), nullable=True),
        sa.Column('observation', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id_plainte', name='pk_plaintes'),
    )
    op.create_index('ix_plaintes_numero_ordre', 'plaintes', ['numero_ordre'])

    # TABLE: proces_verbaux
    op.create_table(
        'proces_verbaux',
        sa.Column('id_pv', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('numero_pv', sa.String(100), nullable=True),
        sa.Column('date_piece', sa.Date(), nullable=True),
        sa.Column('noms_enqueteurs', sa.Text(), nullable=True),
        sa.Column('analyse_sommaire', sa.Text(), nullable=True),
        sa.Column('personne_en_cause', sa.String(255), nullable=True),
        sa.Column('nature_affaire', sa.String(255), nullable=True),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id_pv', name='pk_proces_verbaux'),
    )
    op.create_index('ix_proces_verbaux_numero_pv', 'proces_verbaux', ['numero_pv'])
    op.create_index('ix_proces_verbaux_date_piece', 'proces_verbaux', ['date_piece'])

    # TABLE: services_courants
    op.create_table(
        'services_courants',
        sa.Column('id_service', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('grade_nom', sa.String(255), nullable=True),
        sa.Column('type_arme', sa.String(100), nullable=True),
        sa.Column('tenue', sa.String(100), nullable=True),
        sa.Column('moyen', sa.String(255), nullable=True),
        sa.Column('mission', sa.Text(), nullable=True),
        sa.Column('date_depart', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('date_retour', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('numero_ordre', sa.String(50), nullable=True),
        sa.Column('signataire', sa.String(255), nullable=True),
        sa.CheckConstraint(
            'date_retour IS NULL OR date_depart IS NULL OR date_retour >= date_depart',
            name='ck_services_courants_dates_coherentes'
        ),
        sa.PrimaryKeyConstraint('id_service', name='pk_services_courants'),
    )
    op.create_index('ix_services_courants_date_depart', 'services_courants', ['date_depart'])
    op.create_index('ix_services_courants_numero_ordre', 'services_courants', ['numero_ordre'])

    # TABLE: situations_prise_arme
    op.create_table(
        'situations_prise_arme',
        sa.Column('id_situation', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('effectif_realise', sa.Integer(), nullable=True),
        sa.Column('absent', sa.Integer(), nullable=True),
        sa.Column('present', sa.Integer(), nullable=True),
        sa.Column('indisponible', sa.Integer(), nullable=True),
        sa.Column('sur_le_rang', sa.Integer(), nullable=True),
        sa.Column('motif_absent', sa.Text(), nullable=True),
        sa.Column('motif_indisponible', sa.Text(), nullable=True),
        sa.Column('date_situation', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint('effectif_realise IS NULL OR effectif_realise >= 0', name='ck_situations_effectif_realise_positif'),
        sa.CheckConstraint('absent IS NULL OR absent >= 0', name='ck_situations_absent_positif'),
        sa.CheckConstraint('present IS NULL OR present >= 0', name='ck_situations_present_positif'),
        sa.CheckConstraint('indisponible IS NULL OR indisponible >= 0', name='ck_situations_indisponible_positif'),
        sa.CheckConstraint('sur_le_rang IS NULL OR sur_le_rang >= 0', name='ck_situations_sur_le_rang_positif'),
        sa.PrimaryKeyConstraint('id_situation', name='pk_situations_prise_arme'),
    )
    op.create_index('ix_situations_prise_arme_date_situation', 'situations_prise_arme', ['date_situation'])

    # TABLE: documents
    op.create_table(
        'documents',
        sa.Column('id_document', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('table_source', sa.String(100), nullable=True),
        sa.Column('id_source', sa.BigInteger(), nullable=True),
        sa.Column('categorie_archive', postgresql.ENUM('A', 'B', name='categorie_archive_enum', create_type=False), nullable=False),
        sa.Column('type_document', sa.String(100), nullable=False),
        sa.Column('confidentialite', postgresql.ENUM('NON_CONFIDENTIEL', 'CONFIDENTIEL', name='type_confidentialite_enum', create_type=False), nullable=False),
        sa.Column('mode_conservation', postgresql.ENUM('PHYSIQUE', 'NUMERIQUE', 'MIXTE', name='mode_conservation_enum', create_type=False), nullable=False),
        sa.Column('emplacement_physique', sa.String(500), nullable=True),
        sa.Column('nom_original', sa.String(500), nullable=True),
        sa.Column('nom_interne', sa.String(255), nullable=True),
        sa.Column('extension', sa.String(20), nullable=True),
        sa.Column('mime_type', sa.String(255), nullable=True),
        sa.Column('chemin_stockage', sa.String(1000), nullable=True),
        sa.Column('taille_octets', sa.Integer(), nullable=True),
        sa.Column('sha256', sa.String(64), nullable=True),
        sa.Column('date_import', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('importe_par_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['importe_par_id'], ['utilisateurs.id'], ondelete='SET NULL', name='fk_documents_importe_par_id_utilisateurs'),
        sa.PrimaryKeyConstraint('id_document', name='pk_documents'),
        sa.UniqueConstraint('nom_interne', name='uq_documents_nom_interne'),
    )
    op.create_index('ix_documents_table_source_id_source', 'documents', ['table_source', 'id_source'])
    op.create_index('ix_documents_confidentialite', 'documents', ['confidentialite'])
    op.create_index('ix_documents_date_import', 'documents', ['date_import'])
    op.create_index('ix_documents_importe_par_id', 'documents', ['importe_par_id'])

    # TABLE: historique_actions
    op.create_table(
        'historique_actions',
        sa.Column('id_historique', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('utilisateur_id', sa.BigInteger(), nullable=True),
        sa.Column('identifiant_utilisateur', sa.String(100), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('table_cible', sa.String(100), nullable=True),
        sa.Column('id_enregistrement_cible', sa.String(100), nullable=True),
        sa.Column('date_action', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('adresse_ip', postgresql.INET(), nullable=True),
        sa.Column('succes', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['utilisateurs.id'], ondelete='SET NULL', name='fk_historique_actions_utilisateur_id_utilisateurs'),
        sa.PrimaryKeyConstraint('id_historique', name='pk_historique_actions'),
    )
    op.create_index('ix_historique_actions_date_action', 'historique_actions', ['date_action'])
    op.create_index('ix_historique_actions_utilisateur_id', 'historique_actions', ['utilisateur_id'])
    op.create_index('ix_historique_actions_table_cible', 'historique_actions', ['table_cible'])
    op.create_index('ix_historique_actions_action', 'historique_actions', ['action'])
    op.create_index('ix_historique_actions_succes', 'historique_actions', ['succes'])


def downgrade() -> None:
    op.drop_table('historique_actions')
    op.drop_table('documents')
    op.drop_table('situations_prise_arme')
    op.drop_table('services_courants')
    op.drop_table('proces_verbaux')
    op.drop_table('plaintes')
    op.drop_table('courriers_depart')
    op.drop_table('courriers_arrivee')
    op.drop_table('utilisateurs')
    
    op.execute('DROP TYPE IF EXISTS mode_conservation_enum')
    op.execute('DROP TYPE IF EXISTS type_confidentialite_enum')
    op.execute('DROP TYPE IF EXISTS categorie_archive_enum')
    op.execute('DROP TYPE IF EXISTS statut_utilisateur_enum')
    op.execute('DROP TYPE IF EXISTS role_utilisateur_enum')
