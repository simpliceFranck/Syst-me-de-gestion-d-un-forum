from storage.stockage import storage
from models.message import Message
from services.id_service import id_service
from services.badge_service import badge_service

class MessageService:
    def publier(self, auteur_pseudo, forum_slug, fil_id, texte):
        forum = storage.forums.get(forum_slug)
        if not forum:
            return False, "Forum introuvable."
        fil = next((f for f in forum.fils if f.fil_id == fil_id), None)
        if not fil:
            return False, "Fil introuvable."
        # Déterminer le rôle local (si présent)
        user = storage.utilisateurs.get(auteur_pseudo)
        role_local = user.forums_rejoints.get(forum_slug) if user else None
        # Vérifier le verrouillage du forum/fil
        if forum.verrouille and role_local not in ("admin", "modo"):
            return False, "Forum verrouillé : impossible de publier."
        if fil.verrouille and role_local not in ("admin", "modo"):
            return False, "Ce fil est verrouillé : impossible de publier."
        # Vérifier appartenance (membre ou créateur admin local)
        if role_local not in ("admin", "modo", "membre"):
            return False, "Vous devez être membre pour publier."
        # Création du message
        msg_id = id_service.generer("ME")
        msg = Message(msg_id, auteur_pseudo, texte)
        fil.messages.append(msg)
        # Persistance
        storage.sauvegarder()
        # ---- Badge automatique : compter messages et attribuer si besoin ----
        nouveaux = badge_service.after_message_published(auteur_pseudo)
        # badge_service se charge de créer la notification et de sauvegarder
        return True, f"Message publié (ID = {msg_id})."

    def mod_supprimer_message(self, user_pseudo, forum_slug, fil_id, msg_id):
        forum = storage.forums.get(forum_slug)
        if not forum:
            return False, "Forum introuvable"
        fil = next((f for f in forum.fils if f.fil_id == fil_id), None)
        if not fil:
            return False, "Fil introuvable"
        msg = next((m for m in fil.messages if m.msg_id == msg_id), None)
        if not msg:
            return False, "Message introuvable"
        # Seul admin du forum ou modérateur local peut supprimer
        role = storage.utilisateurs.get(user_pseudo).forums_rejoints.get(forum_slug)
        if role not in ("admin", "modo"):
            return False, "Pas la permission de supprimer ce message"
        fil.messages.remove(msg)
        storage.sauvegarder()
        return True, "Message supprimé"

    def liker(self, user_pseudo, forum_slug, fil_id, msg_id, like=True):
        forum = storage.forums.get(forum_slug)
        if not forum:
            return False, "Forum introuvable"
        fil = next((f for f in forum.fils if f.fil_id == fil_id), None)
        if not fil:
            return False, "Fil introuvable"
        msg = next((m for m in fil.messages if m.msg_id == msg_id), None)
        if not msg:
            return False, "Message introuvable"
        user = storage.utilisateurs.get(user_pseudo)
        role_local = user.forums_rejoints.get(forum_slug) if user else None
        if forum.verrouille and role_local not in ("admin", "modo"):
            return False, "Forum verrouillé : interactions désactivées."
        if fil.verrouille and role_local not in ("admin", "modo"):
            return False, "Fil verrouillé : interactions désactivées."
        if role_local not in ("admin", "modo", "membre"):
            return False, "Vous devez être membre pour liker/disliker."

        # Normaliser sets
        msg.likes = set(msg.likes) if isinstance(msg.likes, (list, tuple, set)) else set()
        msg.dislikes = set(msg.dislikes) if isinstance(msg.dislikes, (list, tuple, set)) else set()

        # Vérifier si l'utilisateur a déjà voté de la même manière
        if like and user_pseudo in msg.likes:
            return False, "Vous avez déjà liké ce message."
        if not like and user_pseudo in msg.dislikes:
            return False, "Vous avez déjà disliké ce message."

        # Supprimer vote contraire si présent
        if like:
            msg.likes.add(user_pseudo)
            msg.dislikes.discard(user_pseudo)
        else:
            msg.dislikes.add(user_pseudo)
            msg.likes.discard(user_pseudo)

        storage.sauvegarder()

        # Évènement : premier like reçu
        if len(msg.likes) == 1:
            auteur = msg.auteur_pseudo
            badge_service.badge_evenement(auteur, "premier_like")

        return True, f"Votre vote a été enregistré (👍 {len(msg.likes)} / 👎 {len(msg.dislikes)})"

    
    def modifier(self, auteur, slug, fil_id, msg_id, nouveau_texte):
        forum = storage.forums.get(slug)
        if not forum:
            return False, "Forum introuvable."
        fil = next((f for f in forum.fils if f.fil_id == fil_id), None)
        if not fil:
            return False, "Fil introuvable."
        msg = next((m for m in fil.messages if m.msg_id == msg_id), None)
        if not msg:
            return False, "Message introuvable."
        user = storage.utilisateurs.get(auteur)
        role_local = user.forums_rejoints.get(forum, "membre")
        est_proprietaire = (msg.auteur_pseudo == auteur)
        if not (est_proprietaire or role_local in ("admin", "modo")):
            return False, "Tu n'as pas la permission de modifier ce message."
        msg.texte = nouveau_texte.strip()
        storage.sauvegarder()
        return True, "Message modifié avec succès."

# instance exportée
message_service = MessageService()