from .fil import Fil

class Forum:
    def __init__(self, forum_id, nom, slug, createur_pseudo):
        self.forum_id = forum_id
        self.nom = nom
        self.slug = slug
        self.admin = createur_pseudo    # pseudo du créateur = admin local
        self.verrouille = False
        self.moderateurs = set()
        self.membres = set([createur_pseudo])
        self.anciens_membres = set()
        self.bannis = set()
        self.fils = []

    def en_dict(self):
        return {
            "forum_id": self.forum_id,
            "nom": self.nom,
            "slug": self.slug,
            "admin": self.admin,
            "verrouille": self.verrouille,
            "moderateurs": list(self.moderateurs),
            "membres": list(self.membres),
            "anciens_membres": list(self.anciens_membres),
            "bannis": list(self.bannis),
            "fils": [f.en_dict() for f in self.fils]
        }

    @staticmethod
    def depuis_dict(d):
        f = Forum(d["forum_id"], d["nom"], d["slug"], d["admin"])
        f.verrouille = d.get("verrouille", False)
        f.moderateurs = set(d.get("moderateurs", []))
        f.membres = set(d.get("membres", []))
        f.anciens_membres = set(d.get("anciens_membres", []))
        f.bannis = set(d.get("bannis", []))
        f.fils = [Fil.depuis_dict(fl) for fl in d.get("fils", [])]
        return f

    def rejoindre(self, pseudo):
        if pseudo in self.bannis:
            return False, "Vous êtes banni de ce forum."
        if self.verrouille:
            return False, "Forum verrouillé : impossible de rejoindre."
        self.membres.add(pseudo)
        return True, "Vous êtes membre du forum."

    def quitter(self, pseudo):
        if pseudo in self.membres:
            self.membres.remove(pseudo)
            self.anciens_membres.add(pseudo)
            return True, "Vous avez quitté le forum."
        return False, "Vous n'êtes pas membre."

    def bannir(self, pseudo):
        if pseudo in self.membres:
            self.membres.discard(pseudo) # on aurait pu aussi utiliser la méthode remove(pseudo)
            self.anciens_membres.add(pseudo)
            self.bannis.add(pseudo)
            # Retirer rôle local dans stockage si existant
            from storage.stockage import storage
            if pseudo in storage.utilisateurs:
                storage.utilisateurs[pseudo].forums_rejoints.pop(self.slug, None)
            return True, f"{pseudo} est banni."
        return False, f"{pseudo} n'est pas membre."

    def ajouter_fil(self, fil):
        self.fils.append(fil)
        return True, "Fil ajouté."

    def nommer_moderateur(self, pseudo):
        if pseudo in self.membres:
            self.moderateurs.add(pseudo)
            return True, "Modérateur nommé."
        return False, "L'utilisateur doit être membre."

    def verrouiller(self):
        if self.verrouille:
            return False, "Forum déjà verrouillé."
        self.verrouille = True
        return True, "Forum verrouillé : seuls admin/modos peuvent agir."

    def deverrouiller(self):
        if not self.verrouille:
            return False, "Forum déjà déverrouillé."
        self.verrouille = False
        return True, "Forum déverrouillé."

    def debannir(self, pseudo):
        """
        Rétablit un utilisateur banni comme membre du forum.
        Si l'utilisateur n'était pas banni, la méthode ne fait rien.
        Si l'utilisateur n'existe pas dans le stockage global, on ignore simplement.
        """
        from storage.stockage import storage
        # 1) Si l'utilisateur n'est pas banni → aucun effet
        if pseudo not in self.bannis:
            return False, f"{pseudo} n'était pas banni."
        # 2) Retrait des listes de bannis + anciens membres
        self.bannis.discard(pseudo)
        self.anciens_membres.discard(pseudo)
        # 3) Retour parmi les membres du forum
        self.membres.add(pseudo)
        # 4) Si l'utilisateur existe dans le stockage → mettre à jour son rôle local
        utilisateur = storage.utilisateurs.get(pseudo)
        if utilisateur:
            utilisateur.forums_rejoints[self.slug] = "membre"
            return True, f"{pseudo} a été réintégré comme membre."