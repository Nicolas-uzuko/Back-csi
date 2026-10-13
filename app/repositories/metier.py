from app.models.courrier_arrivee import CourrierArrivee
from app.models.courrier_depart import CourrierDepart
from app.models.plainte import Plainte
from app.models.proces_verbal import ProcesVerbal
from app.models.service_courant import ServiceCourant
from app.models.situation_prise_arme import SituationPriseArme
from app.repositories.base import AsyncRepository


class CourrierArriveeRepository(AsyncRepository[CourrierArrivee]):
    model = CourrierArrivee
    id_field = "id_courrier"


class CourrierDepartRepository(AsyncRepository[CourrierDepart]):
    model = CourrierDepart
    id_field = "id_courrier"


class PlainteRepository(AsyncRepository[Plainte]):
    model = Plainte
    id_field = "id_plainte"


class ProcesVerbalRepository(AsyncRepository[ProcesVerbal]):
    model = ProcesVerbal
    id_field = "id_pv"


class ServiceCourantRepository(AsyncRepository[ServiceCourant]):
    model = ServiceCourant
    id_field = "id_service"


class SituationPriseArmeRepository(AsyncRepository[SituationPriseArme]):
    model = SituationPriseArme
    id_field = "id_situation"
