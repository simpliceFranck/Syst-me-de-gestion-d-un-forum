import os, hashlib, base64

class Securite:
    @staticmethod
    def generer_sel():
        return base64.b64encode(os.urandom(16)).decode()

    @staticmethod
    def hacher_mot_de_passe(mdp, sel=None):
        if not sel:
            sel = Securite.generer_sel()
        sel_bytes = base64.b64decode(sel.encode())
        hash_bytes = hashlib.pbkdf2_hmac('sha256', mdp.encode(), sel_bytes, 120000)
        return base64.b64encode(hash_bytes).decode(), sel

    @staticmethod
    def verifier_mot_de_passe(mdp, mdp_hash, sel):
        test_hash, _ = Securite.hacher_mot_de_passe(mdp, sel)
        return test_hash == mdp_hash