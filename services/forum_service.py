from services.id_service import id_service
from storage.stockage import storage
from utils.slug import Slug
from models.forum import Forum
from services.badge_service import badge_service

class ForumService:
    def creer_forum(self, createur_pseudo, nom_forum):
        if not nom_forum:
            return False, "Nom invalide."
        slug = Slug.vers_slug(nom_forum)
        if slug in storage.forums:
            return False, "Forum existe déjà."
        forum_id = id_service.generer("FO")
        forum = Forum(forum_id, nom_forum, slug, createur_pseudo)
        storage.forums[slug] = forum
        # Mettre à jour l'utilisateur créateur : devient admin local
        user = storage.utilisateurs.get(createur_pseudo)
        if user:
            user.forums_crees.append(slug)
            user.forums_rejoints[slug] = "admin"
        storage.sauvegarder()
        # Badge événementiel : création de forum
        badge_service.after_forum_created(createur_pseudo)
        return True, f"Forum créé (slug = {slug})."

    def lister_forums(self):
        if not storage.forums:
            return False, "Aucun forum disponible."
        lines = [f"{i+1} - {f.nom} (slug = {f.slug})" for i,f in enumerate(storage.forums.values())]
        if len(lines) == 1:
            lines = lines = [f"{f.nom} (slug = {f.slug})" for f in storage.forums.values()]
        return True, "\n".join(lines)

    def get_forum(self, slug):
        return storage.forums.get(slug)

forum_service = ForumService()