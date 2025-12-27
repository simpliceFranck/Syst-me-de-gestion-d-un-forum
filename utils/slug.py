import re
import unicodedata

class Slug:
    @staticmethod
    def vers_slug(nom):
        nom = nom.lower().strip()
        nom = unicodedata.normalize('NFD', nom)
        nom = ''.join(ch for ch in nom if unicodedata.category(ch) != 'Mn')
        nom = re.sub(r'[^a-z0-9 ]+', '', nom)
        nom = "SL-" + re.sub(r'\s+', '-', nom).strip('-')
        return nom