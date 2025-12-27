class Categorie:
    def __init__(self, cat_id, nom):
        self.cat_id = cat_id
        self.nom = nom

    def to_dict(self):
        return {"cat_id": self.cat_id, "nom": self.nom}

    @staticmethod
    def from_dict(d):
        return Categorie(d["cat_id"], d["nom"])