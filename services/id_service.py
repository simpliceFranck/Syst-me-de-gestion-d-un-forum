import uuid

class IDService:
    def generer(self, prefixe="ID"):
        unique = uuid.uuid4().hex[:12]
        return f"{prefixe}_{unique}"

id_service = IDService()