from app.models.historique_action import HistoriqueAction
from app.repositories.base import AsyncRepository


class AuditRepository(AsyncRepository[HistoriqueAction]):
    model = HistoriqueAction
    id_field = "id_historique"
