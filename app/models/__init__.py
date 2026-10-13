# Import all models so Alembic can discover them
from app.models.utilisateur import Utilisateur  # noqa: F401
from app.models.courrier_arrivee import CourrierArrivee  # noqa: F401
from app.models.courrier_depart import CourrierDepart  # noqa: F401
from app.models.plainte import Plainte  # noqa: F401
from app.models.proces_verbal import ProcesVerbal  # noqa: F401
from app.models.service_courant import ServiceCourant  # noqa: F401
from app.models.situation_prise_arme import SituationPriseArme  # noqa: F401
from app.models.document import Document  # noqa: F401
from app.models.historique_action import HistoriqueAction  # noqa: F401
