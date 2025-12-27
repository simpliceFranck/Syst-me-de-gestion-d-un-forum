from storage import storage
from utils.couleurs import print_ok, print_err

class CategorieService:
    def creer_categorie(self, forum_slug: str, nom_categorie: str):
        f = storage.get_forum(forum_slug)
        if not f:
            print_err("Forum introuvable")
            return False
        if nom_categorie in f.categories:
            print_err("Catégorie déjà existante")
            return False
        f.categories.append(nom_categorie)
        storage.update_forum(f)
        print_ok("Catégorie créée")
        return True

categorie_service = CategorieService()