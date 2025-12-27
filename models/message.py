class Message:
    def __init__(self, msg_id, auteur_pseudo, texte):
        self.msg_id = msg_id
        self.auteur_pseudo = auteur_pseudo
        self.texte = texte
        self.likes = set()
        self.dislikes = set()

    def en_dict(self):
        return {
            "msg_id": self.msg_id,
            "auteur_pseudo": self.auteur_pseudo,
            "texte": self.texte,
            "likes": list(self.likes),
            "dislikes": list(self.dislikes)
        }

    @staticmethod
    def depuis_dict(d):
        m = Message(d["msg_id"], d["auteur_pseudo"], d["texte"])
        m.likes = set(d.get("likes", []))
        m.dislikes = set(d.get("dislikes", []))
        return m