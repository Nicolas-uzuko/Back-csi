from datetime import datetime, timedelta, timezone
from io import BytesIO

import pytest
from fastapi import UploadFile
from jose import JWTError, jwt

from app.core.config import settings
from app.core.permissions import Permission, has_permission
from app.core.security import generate_reset_token, hash_password, verify_password, verify_reset_token
from app.models.utilisateur import RoleUtilisateur, StatutUtilisateur, Utilisateur
from app.services.audit import redact_details
from app.services.storage import PrivateFileStorage


def user(role):
    return Utilisateur(
        id=1,
        nom="Test",
        nom_utilisateur="test",
        email="test@example.com",
        mot_de_passe_hash="not-used",
        role=role,
        statut=StatutUtilisateur.ACTIF,
    )


def test_sensitive_permissions_are_not_implied_by_authenticated_role():
    ordinary = user(RoleUtilisateur.UTILISATEUR)
    assert not has_permission(ordinary, Permission.PLAINTES_LECTURE)
    assert not has_permission(ordinary, Permission.PV_LECTURE)
    assert not has_permission(ordinary, Permission.DOCUMENTS_B_LECTURE)
    assert not has_permission(ordinary, Permission.AUDIT_LECTURE)
    assert has_permission(ordinary, Permission.COURRIERS_ARRIVEE_LECTURE)
    assert has_permission(user(RoleUtilisateur.ADMIN), Permission.PV_SUPPRESSION)


def test_reset_token_is_random_and_only_hash_is_needed_for_verification():
    clear, stored_hash = generate_reset_token()
    assert clear != stored_hash
    assert verify_reset_token(clear, stored_hash)
    assert not verify_reset_token(clear + "x", stored_hash)


def test_password_hash_does_not_truncate_allowed_long_passwords():
    password = "A1" + "x" * 120
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password(password + "x", hashed)


def test_expired_jwt_is_rejected():
    token = jwt.encode(
        {"sub": "1", "type": "access", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    from app.core.security import decode_token

    with pytest.raises(JWTError):
        decode_token(token)


def test_audit_redacts_credentials_and_document_content():
    details = redact_details({"mot_de_passe": "secret", "reset_token": "token", "contenu": "full confidential text", "ok": "value"})
    assert details["mot_de_passe"] == "[REDACTE]"
    assert details["reset_token"] == "[REDACTE]"
    assert details["contenu"] == "[CONTENU_NON_JOURNALISE]"
    assert details["ok"] == "value"


@pytest.mark.asyncio
async def test_dangerous_upload_is_rejected_and_valid_file_is_private(tmp_path):
    storage = PrivateFileStorage(tmp_path)
    dangerous = UploadFile(filename="malware.pdf", file=BytesIO(b"MZ\x90\x00not a pdf"))
    with pytest.raises(ValueError):
        await storage.save_upload(dangerous)

    valid = UploadFile(filename="courrier.pdf", file=BytesIO(b"%PDF-1.4\nminimal"), headers={"content-type": "application/pdf"})
    saved = await storage.save_upload(valid)
    assert str(tmp_path) in str(saved["chemin_stockage"])
    assert not (tmp_path / str(saved["nom_original"])).exists()
