from .message import Message

class Fil:
    def __init__(self, fil_id, titre, createur_pseudo):
        self.fil_id = fil_id
        self.titre = titre
        self.createur = createur_pseudo
        self.verrouille = False
        self.messages = []  # liste d'objets Message

    def en_dict(self):
        return {
            "fil_id": self.fil_id,
            "titre": self.titre,
            "createur": self.createur,
            "verrouille": self.verrouille,
            "messages": [m.en_dict() for m in self.messages]
        }

    @staticmethod
    def depuis_dict(d):
        f = Fil(d["fil_id"], d["titre"], d.get("createur", ""))
        f.verrouille = d.get("verrouille", False)
        f.messages = [Message.depuis_dict(m) for m in d.get("messages", [])]
        return f