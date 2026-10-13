from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.db.base import Base
from app.models.document import CategorieArchive, ModeConservation, TypeConfidentialite
from app.schemas.courrier_arrivee import CourrierArriveeCreate
from app.schemas.courrier_depart import CourrierDepartCreate
from app.schemas.document import DocumentCreate, DocumentUploadMetadata
from app.schemas.service_courant import ServiceCourantCreate
from app.schemas.situation_prise_arme import SituationPriseArmeCreate
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurRead


def test_business_fields_and_identity_columns_are_explicit():
    assert "entete_message" not in Base.metadata.tables["courriers_arrivee"].columns
    assert "entete_message" not in Base.metadata.tables["courriers_depart"].columns
    for table in Base.metadata.tables.values():
        primary_key = next(iter(table.primary_key.columns))
        assert primary_key.identity is not None, table.name


def test_categories_are_validated_without_inventing_meanings():
    with pytest.raises(ValidationError):
        CourrierArriveeCreate(categorie="/9", categorie_archive="A")
    with pytest.raises(ValidationError):
        CourrierDepartCreate(categorie="/3", categorie_archive="A")
    # FM/TO/INFO/REF are retained as opaque business labels.
    item = CourrierDepartCreate(categorie="/2", categorie_archive="A", fm="FM", to="TO", info="INFO", ref="REF")
    assert item.fm == "FM" and item.to == "TO" and item.info == "INFO" and item.ref == "REF"


def test_counters_cannot_be_negative_but_are_not_forced_equal():
    with pytest.raises(ValidationError):
        SituationPriseArmeCreate(absent=-1)
    item = SituationPriseArmeCreate(effectif_realise=10, present=2, absent=99)
    assert item.absent == 99


def test_service_dates_are_coherent():
    start = datetime(2026, 1, 2, tzinfo=timezone.utc)
    with pytest.raises(ValidationError):
        ServiceCourantCreate(date_depart=start, date_retour=start - timedelta(minutes=1))


def test_password_is_not_part_of_read_schema():
    user = UtilisateurCreate(
        nom="Doe",
        nom_utilisateur="jdoe",
        email="jdoe@example.com",
        mot_de_passe="Motdepasse1",
    )
    assert "mot_de_passe" not in UtilisateurRead.model_fields
    assert user.mot_de_passe == "Motdepasse1"


def test_archive_metadata_has_single_physical_and_upload_paths():
    physical = DocumentCreate(
        categorie_archive=CategorieArchive.A,
        type_document="CORRESPONDANCE_ARRIVEE_3",
        confidentialite=TypeConfidentialite.NON_CONFIDENTIEL,
        mode_conservation=ModeConservation.PHYSIQUE,
        emplacement_physique="Armoire A / boîte 1",
    )
    assert physical.mode_conservation == ModeConservation.PHYSIQUE
    with pytest.raises(ValidationError):
        DocumentCreate(
            categorie_archive=CategorieArchive.A,
            type_document="CORRESPONDANCE_ARRIVEE_3",
            confidentialite=TypeConfidentialite.NON_CONFIDENTIEL,
            mode_conservation=ModeConservation.NUMERIQUE,
        )
    with pytest.raises(ValidationError):
        DocumentUploadMetadata(
            categorie_archive=CategorieArchive.A,
            type_document="ARCHIVE_PROCES_VERBAL",
            confidentialite=TypeConfidentialite.NON_CONFIDENTIEL,
            mode_conservation=ModeConservation.NUMERIQUE,
        )
