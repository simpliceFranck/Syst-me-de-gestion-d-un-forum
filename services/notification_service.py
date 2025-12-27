"""
services/notification_service.py
Service pour créer/consulter/marquer notifications.
Utilise storage utilitaires et sauvegarde via storage.sauvegarder().
"""

from storage.stockage import storage

class NotificationService:
    def creer_notification(self, pseudo, texte):
        """
        Ajoute une notification non lue à l'utilisateur pseudo.
        Retourne (ok, msg)
        """
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return False, "Utilisateur introuvable."
        if not hasattr(user, "notifications") or user.notifications is None:
            user.notifications = []
        notif = {"texte": texte, "lu": False}
        user.notifications.append(notif)
        storage.sauvegarder()
        return True, "Notification créée."

    def lister_non_lues(self, pseudo):
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return False, []
        notifs = [n for n in (user.notifications or []) if not n.get("lu", False)]
        return True, notifs

    def marquer_lues(self, pseudo):
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return False, "Utilisateur introuvable."
        for n in (user.notifications or []):
            n["lu"] = True
        storage.sauvegarder()
        return True, "Notifications marquées lues."
    
    # utilitaire : suppression d'une notification spécifique (optionnel)
    def supprimer_notification(self, pseudo, index):
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return False, "Utilisateur introuvable."
        try:
            del user.notifications[index]
            storage.sauvegarder()
            return True, "Notification supprimée."
        except Exception:
            return False, "Index invalide."

notification_service = NotificationService()