from app.models.document import Document
from app.repositories.base import AsyncRepository


class DocumentRepository(AsyncRepository[Document]):
    model = Document
    id_field = "id_document"
