import asyncio
import hashlib
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Dict, Optional, Union

from fastapi import UploadFile

from app.core.config import settings

try:
    import magic  # type: ignore
except ImportError:  # pragma: no cover - optional platform dependency
    magic = None


ALLOWED_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/tiff",
        "text/plain",
        "application/rtf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }
)
DANGEROUS_EXTENSIONS = frozenset({".exe", ".dll", ".bat", ".cmd", ".com", ".ps1", ".js", ".mjs", ".php", ".sh", ".html", ".svg"})
PRIVATE_NAME_RE = re.compile(r"^[0-9a-f-]{36}\.[a-z0-9]{1,10}$")


def detect_mime(content: bytes, declared: Optional[str]) -> str:
    if content.startswith(b"MZ") or content.startswith(b"#!"):
        raise ValueError("Fichier executable ou script interdit")
    detected = None
    if magic is not None:
        try:
            detected = magic.from_buffer(content[:8192], mime=True)
        except Exception:
            detected = None
    if detected in {"application/zip", "application/octet-stream"} and declared in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    }:
        detected = declared
    if detected not in ALLOWED_MIME_TYPES:
        detected = declared if declared in ALLOWED_MIME_TYPES else None
    if detected is None:
        raise ValueError("Type MIME de fichier non autorise")
    return detected


class PrivateFileStorage:
    def __init__(self, root: Optional[Union[str, Path]] = None):
        self.root = Path(root or settings.private_storage_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload: UploadFile) -> Dict[str, Union[str, int]]:
        original_name = Path(upload.filename or "document").name
        extension = Path(original_name).suffix.lower()
        if extension in DANGEROUS_EXTENSIONS:
            raise ValueError("Extension de fichier interdite")
        content = await upload.read(settings.max_upload_size_bytes + 1)
        if not content:
            raise ValueError("Le fichier est vide")
        if len(content) > settings.max_upload_size_bytes:
            raise ValueError("Fichier trop volumineux")
        mime_type = detect_mime(content, upload.content_type)
        if not extension:
            extension = mimetypes.guess_extension(mime_type) or ".bin"
        extension = extension.lstrip(".")[:10].lower()
        internal_name = f"{uuid.uuid4()}.{extension}"
        destination = (self.root / internal_name).resolve()
        if destination.parent != self.root or not PRIVATE_NAME_RE.fullmatch(internal_name):
            raise ValueError("Nom interne de fichier invalide")
        await asyncio.to_thread(destination.write_bytes, content)
        return {
            "nom_original": original_name[:500],
            "nom_interne": internal_name,
            "extension": extension,
            "mime_type": mime_type,
            "chemin_stockage": str(destination),
            "taille_octets": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }

    async def read_private(self, path: str) -> bytes:
        candidate = Path(path).resolve()
        if candidate.parent != self.root:
            raise ValueError("Chemin de stockage hors espace prive")
        if not candidate.is_file():
            raise FileNotFoundError
        return await asyncio.to_thread(candidate.read_bytes)


private_storage = PrivateFileStorage()
