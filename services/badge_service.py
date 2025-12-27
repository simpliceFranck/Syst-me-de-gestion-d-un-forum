"""
services/badge_service.py
Service de gestion des badges.
- Lit une configuration JSON optionnelle (data/badges.json)
- Permet d'attribuer des badges (activité + événements)
- Crée automatiquement une notification lorsqu'un badge est attribué
"""

import os
import json
from storage.stockage import storage
from services.notification_service import notification_service

# Emplacement optionnel du fichier de configuration des badges
BADGES_CONFIG_PATH = os.path.join("data", "badges.json")
# Configuration par défaut (utilisée si badges.json absent)
DEFAULT_CONFIG = {
    "activite": {
        # clé "messages": seuils -> libellé
        "messages": {
            "1": "Nouveau contributeur",
            "10": "Participant régulier",
            "100": "Pilier du forum"
        }
    },
    "evenements": {
        "creation_forum": "Fondateur",
        "creation_fil": "Créateur de discussions",
        "premier_like": "Apprécié"
    }
}

class BadgeService:
    def __init__(self):
        self.config = self._charger_config()

    def _charger_config(self):
        if os.path.exists(BADGES_CONFIG_PATH):
            try:
                with open(BADGES_CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                # Normalisation simple si clés manquantes
                cfg.setdefault("activite", {}).setdefault("messages", {})
                cfg.setdefault("evenements", {})
                return cfg
            except Exception:
                # En cas d'erreur de lecture, utiliser la config par défaut
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def _a_deja_badge(self, user, badge_label):
        return badge_label in (user.badges or [])

    def _attribuer_badge(self, pseudo, badge_label):
        """
        Attribue le badge (libellé) à l'utilisateur pseudo s'il ne l'a pas déjà,
        crée une notification et sauvegarde.
        Retourne (ok, msg)
        """
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return False, "Utilisateur introuvable."
        if not hasattr(user, "badges") or user.badges is None:
            user.badges = []
        if self._a_deja_badge(user, badge_label):
            return False, "Badge déjà attribué."

        user.badges.append(badge_label)
        # Notification automatique
        notif_text = f"Nouveau badge : {badge_label}"
        notification_service.creer_notification(pseudo, notif_text)
        # Persistance
        storage.sauvegarder()
        return True, f"Badge attribué : {badge_label}"

    def _compter_messages(self, pseudo):
        """Compter le nombre total de messages d'un pseudo dans tous les forums."""
        total = 0
        for forum in storage.forums.values():
            for fil in forum.fils:
                for msg in fil.messages:
                    try:
                        if msg.auteur_pseudo == pseudo:
                            total += 1
                    except Exception:
                        # champ absent ou atypique : ignorer
                        pass
        return total

    def verifier_badges_messages(self, pseudo):
        """
        Vérifie les seuils de messages définis dans la config et attribue les nouveaux badges.
        Retourne une liste des badges nouvellement attribués.
        """
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return []

        seuils_cfg = self.config.get("activite", {}).get("messages", {})
        if not seuils_cfg:
            return []

        # convertir clés en int et trier
        try:
            seuils = sorted(int(k) for k in seuils_cfg.keys())
        except Exception:
            seuils = []

        nb = self._compter_messages(pseudo)
        badges_attribues = []
        for s in seuils:
            if nb >= s:
                label = seuils_cfg.get(str(s))
                if label and not self._a_deja_badge(user, label):
                    ok, _ = self._attribuer_badge(pseudo, label)
                    if ok:
                        badges_attribues.append(label)
        return badges_attribues

    def badge_evenement(self, pseudo, evenement):
        user = storage.utilisateurs.get(pseudo)
        if not user:
            return False, "Utilisateur introuvable."
        label = self.config.get("evenements", {}).get(evenement)
        if not label:
            return False, "Événement inconnu."
        return self._attribuer_badge(pseudo, label)

    def after_message_published(self, pseudo):
        """
        À appeler juste après la publication d'un message.
        Vérifie les badges d'activité (messages) et retourne la liste des nouveaux badges.
        """
        return self.verifier_badges_messages(pseudo)

    def after_forum_created(self, pseudo):
        attribues = []
        ok, _ = self.badge_evenement(pseudo, "creation_forum")
        if ok:
            attribues.append(self.config.get("evenements", {}).get("creation_forum"))
        # possibilité d'ajouter d'autres événements ici
        return attribues

    def after_fil_created(self, pseudo):
        ok, _ = self.badge_evenement(pseudo, "creation_fil")
        return [self.config.get("evenements", {}).get("creation_fil")] if ok else []

# instance exportée
badge_service = BadgeService()