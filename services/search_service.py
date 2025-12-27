from storage.stockage import storage

class SearchService:
    def rechercher(self, texte):
        if not texte or not texte.strip():
            return False, "Texte de recherche vide."
        t = texte.lower()
        resultats = []
        for forum in storage.forums.values():
            for fil in forum.fils:
                for msg in fil.messages:
                    if t in msg.texte.lower():
                        resultats.append({"forum": forum.slug, "fil": fil.titre, "auteur": msg.auteur_pseudo, "texte": msg.texte})
        if not resultats:
            return False, "Aucun résultat."
        return True, resultats

search_service = SearchService()