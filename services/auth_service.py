from utils.securite import Securite
from services.id_service import id_service
from storage.stockage import storage
from models.utilisateur import Utilisateur

class AuthService:
    def inscription(self, pseudo, mdp):
        if not pseudo or not mdp:
            return False, "Pseudo et mot de passe requis."
        if pseudo in storage.utilisateurs:
            return False, "Pseudo déjà utilisé."
        mdp_hash, sel = Securite.hacher_mot_de_passe(mdp)
        user_id = id_service.generer("US")
        u = Utilisateur(user_id, pseudo, mdp_hash, sel)
        storage.utilisateurs[pseudo] = u
        storage.sauvegarder()
        return True, "Inscription réussie."

    def connexion(self, pseudo, mdp):
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return False, "Utilisateur introuvable."
        if not Securite.verifier_mot_de_passe(mdp, user.mdp_hash, user.sel):
            return False, "Mot de passe incorrect."
        return True, "Connexion réussie."

auth_service = AuthService()