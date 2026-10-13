from collections.abc import Mapping
from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.historique_action import HistoriqueAction
from app.repositories.audit import AuditRepository


_SECRET_WORDS = ("password", "mot_de_passe", "token", "secret", "hash")


def redact_details(value: Any, *, depth: int = 0) -> Any:
    """Keep audit context useful without persisting credentials or full documents."""
    if depth > 3:
        return "[TRONQUE]"
    if isinstance(value, Mapping):
        result = {}
        for key, item in value.items():
            key_text = str(key)
            if any(word in key_text.lower() for word in _SECRET_WORDS):
                result[key_text] = "[REDACTE]"
            elif key_text.lower() in {"contenu", "content", "document", "document_content"}:
                result[key_text] = "[CONTENU_NON_JOURNALISE]"
            else:
                result[key_text] = redact_details(item, depth=depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        return [redact_details(item, depth=depth + 1) for item in value[:20]]
    if isinstance(value, str):
        return value[:1000]
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return str(value)[:1000]


class AuditService:
    async def log(
        self,
        db: AsyncSession,
        *,
        action: str,
        user_id: Optional[int] = None,
        identifier: Optional[str] = None,
        table: Optional[str] = None,
        record_id: Optional[Union[int, str]] = None,
        details: Optional[Mapping[str, Any]] = None,
        ip_address: Optional[str] = None,
        success: Optional[bool] = None,
        independent_commit: bool = False,
    ) -> None:
        values = {
            "utilisateur_id": user_id,
            "identifiant_utilisateur": identifier,
            "action": action[:50],
            "table_cible": table[:100] if table else None,
            "id_enregistrement_cible": str(record_id)[:100] if record_id is not None else None,
            "details": redact_details(details) if details is not None else None,
            "adresse_ip": ip_address,
            "succes": success,
        }
        if independent_commit:
            async with AsyncSessionLocal() as audit_db:
                audit_db.add(HistoriqueAction(**values))
                await audit_db.commit()
        else:
            db.add(HistoriqueAction(**values))
            await db.flush()


audit_service = AuditService()
