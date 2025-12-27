class Utilisateur:
    def __init__(self, user_id, pseudo, mdp_hash, sel):
        self.user_id = user_id
        self.pseudo = pseudo
        self.mdp_hash = mdp_hash
        self.sel = sel
        self.badges = []
        self.notifications = []   # {"texte": "...", "lu": False}
        self.inbox = []           # messages privés reçus
        self.outbox = []          # messages privés envoyés
        self.forums_rejoints = {} # slug -> role local ("admin","modo","membre")
        self.forums_crees = []    # slugs

    def en_dict(self):
        return {
            "user_id": self.user_id,
            "pseudo": self.pseudo,
            "mdp_hash": self.mdp_hash,
            "sel": self.sel,
            "badges": list(self.badges),
            "notifications": list(self.notifications),
            "inbox": list(self.inbox),
            "outbox": list(self.outbox),
            "forums_rejoints": dict(self.forums_rejoints),
            "forums_crees": list(self.forums_crees)
        }

    @staticmethod
    def depuis_dict(d):
        u = Utilisateur(d["user_id"], d["pseudo"], d["mdp_hash"], d["sel"])
        u.badges = list(d.get("badges", []))
        u.notifications = list(d.get("notifications", []))
        u.inbox = list(d.get("inbox", []))
        u.outbox = list(d.get("outbox", []))
        u.forums_rejoints = dict(d.get("forums_rejoints", {}))
        u.forums_crees = list(d.get("forums_crees", []))
        return u