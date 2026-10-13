from enum import Enum

from app.models.utilisateur import RoleUtilisateur, Utilisateur


class Permission(str, Enum):
    UTILISATEURS_LECTURE = "utilisateurs:lecture"
    UTILISATEURS_ECRITURE = "utilisateurs:ecriture"
    ROLES_MODIFICATION = "roles:modification"
    COURRIERS_ARRIVEE_LECTURE = "courriers_arrivee:lecture"
    COURRIERS_ARRIVEE_ECRITURE = "courriers_arrivee:ecriture"
    COURRIERS_DEPART_LECTURE = "courriers_depart:lecture"
    COURRIERS_DEPART_ECRITURE = "courriers_depart:ecriture"
    SERVICES_LECTURE = "services:lecture"
    SERVICES_ECRITURE = "services:ecriture"
    SITUATIONS_LECTURE = "situations:lecture"
    SITUATIONS_ECRITURE = "situations:ecriture"
    PLAINTES_LECTURE = "plaintes:lecture"
    PLAINTES_ECRITURE = "plaintes:ecriture"
    PLAINTES_SUPPRESSION = "plaintes:suppression"
    PV_LECTURE = "pv:lecture"
    PV_TELECHARGEMENT = "pv:telechargement"
    PV_ECRITURE = "pv:ecriture"
    PV_SUPPRESSION = "pv:suppression"
    DOCUMENTS_A_LECTURE = "documents:a:lecture"
    DOCUMENTS_B_LECTURE = "documents:b:lecture"
    DOCUMENTS_ECRITURE = "documents:ecriture"
    DOCUMENTS_SUPPRESSION = "documents:suppression"
    AUDIT_LECTURE = "audit:lecture"


# The only roles required by the design are ADMIN and UTILISATEUR. Sensitive
# permissions are intentionally separate: a general authenticated role does
# not grant access to complaints, PVs, category B, or the audit log.
ORDINARY_PERMISSIONS = frozenset(
    {
        Permission.COURRIERS_ARRIVEE_LECTURE,
        Permission.COURRIERS_ARRIVEE_ECRITURE,
        Permission.COURRIERS_DEPART_LECTURE,
        Permission.COURRIERS_DEPART_ECRITURE,
        Permission.SERVICES_LECTURE,
        Permission.SERVICES_ECRITURE,
        Permission.SITUATIONS_LECTURE,
        Permission.SITUATIONS_ECRITURE,
        Permission.DOCUMENTS_A_LECTURE,
    }
)


def has_permission(user: Utilisateur, permission: Permission) -> bool:
    if user.role == RoleUtilisateur.ADMIN:
        return True
    return permission in ORDINARY_PERMISSIONS
