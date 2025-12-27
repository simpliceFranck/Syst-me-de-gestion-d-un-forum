from storage.stockage import storage
from services.id_service import id_service

class MpService:
    def envoyer_mp(self, expediteur_pseudo, destinataire_pseudo, texte):
        dest = storage.utilisateurs.get(destinataire_pseudo)
        if not dest:
            return False, "Destinataire introuvable."
        mp_id = id_service.generer("MP")
        mp = {"mp_id": mp_id, "texte": texte, "de": expediteur_pseudo, "lu": False}
        dest.inbox.append(mp)
        exp = storage.utilisateurs.get(expediteur_pseudo)
        if exp:
            exp.outbox.append(mp)
        storage.sauvegarder()
        return True, f"MP envoyé (ID = {mp_id})."

mp_service = MpService()