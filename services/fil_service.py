from storage.stockage import storage
from utils.roles import role_local
from models.fil import Fil
from services.id_service import id_service
from services.badge_service import badge_service

class FilService:
    def creer_fil(self, auteur_pseudo, forum_slug, titre):
        titre = (titre or "").strip()
        forum = storage.forums.get(forum_slug)
        if not forum:
            return False, "Forum introuvable."
        rl = role_local(auteur_pseudo, forum_slug)
        if forum.verrouille and rl not in ("admin","modo"):
            return False, "Forum verrouillé : impossible de créer un fil."
        if rl not in ("admin","modo","membre"):
            return False, "Vous devez être membre pour créer un fil."
        fil_id = id_service.generer("FI")
        fil = Fil(fil_id, titre, auteur_pseudo)
        forum.fils.append(fil)
        storage.sauvegarder()

        # badge événementiel
        badge_service.after_fil_created(auteur_pseudo)

        return True, f"Fil créé (ID={fil_id})."

fil_service = FilService()