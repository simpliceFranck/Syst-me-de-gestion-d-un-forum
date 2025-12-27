import json
import os
import shutil
from models.utilisateur import Utilisateur
from models.forum import Forum
from utils.couleurs import couleur

DATA_FILE = r"C:\Users\franc\MesProjets\GestionForumAvance\storage\data.json"
BACKUP_FILE = r"C:\Users\franc\MesProjets\GestionForumAvance\storage\data.json.bak"

class Stockage:
    def __init__(self):
        self.forums = {}            # slug -> Forum
        self.utilisateurs = {}      # pseudo -> Utilisateur
        self.forums_supprimes = {}  # slug -> dict

    def charger(self):
        if not os.path.exists(DATA_FILE):
            # couleur.print_jaune("[Stockage] data.json introuvable → création d'un fichier neuf.")
            self.sauvegarder()
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            couleur.print_rouge("[Stockage] data.json corrompu ou introuvable. Réinitialisation.")
            data = {"utilisateurs": [], "forums": [], "forums_supprimes": {}}
            self.sauvegarder()
        self.utilisateurs = {u["pseudo"]: Utilisateur.depuis_dict(u) for u in data.get("utilisateurs", [])}
        self.forums = {d["slug"]: Forum.depuis_dict(d) for d in data.get("forums", [])}
        self.forums_supprimes = data.get("forums_supprimes", {})

    def sauvegarder(self):
        data = {
            "utilisateurs": [u.en_dict() for u in self.utilisateurs.values()],
            "forums": [f.en_dict() for f in self.forums.values()],
            "forums_supprimes": self.forums_supprimes
        }
        if os.path.exists(DATA_FILE):
            try:
                shutil.copy(DATA_FILE, BACKUP_FILE)
            except Exception:
                pass
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # couleur.print_jaune("[Stockage] Sauvegarde effectuée.")

storage = Stockage()