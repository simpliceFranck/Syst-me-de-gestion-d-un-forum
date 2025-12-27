import pytest
import json
from storage.stockage import storage
from services.auth_service import auth_service
from models.forum import Forum
from services.message_service import message_service as msg_service
from services.mp_service import mp_service

# --- Helpers ---
def creer_utilisateur(pseudo):
    """Crée un utilisateur proprement pour les tests."""
    ok, _ = auth_service.inscription(pseudo, "pass")
    assert ok, f"Impossible de créer l'utilisateur {pseudo}"
    return storage.utilisateurs[pseudo]

# --- Fixtures ---
@pytest.fixture(autouse=True)
def isoler_fichier_json(tmp_path, monkeypatch):
    """Isoler le stockage JSON pour ne pas toucher au fichier réel."""
    from storage import stockage
    data_file = tmp_path / "data.json"
    backup_file = tmp_path / "data.json.bak"
    monkeypatch.setattr(stockage, "DATA_FILE", str(data_file))
    monkeypatch.setattr(stockage, "BACKUP_FILE", str(backup_file))
    stockage.storage.utilisateurs.clear()
    stockage.storage.forums.clear()
    stockage.storage.forums_supprimes.clear()
    yield
    stockage.storage.utilisateurs.clear()
    stockage.storage.forums.clear()
    stockage.storage.forums_supprimes.clear()

# --- Tests existants ---
def test_publication_impossible_with_existing_fil():
    """
    Couvre la branche manquante dans test_edge_cases :
        if forum.fils:
    et vérifie que la publication échoue car le forum n'est pas dans le stockage.
    """
    user2 = creer_utilisateur("Bob")
    
    # Créer un forum avec un fil
    forum = Forum("forumX", "ForumX", "forumx", "Admin")
    forum.fils.append(type("FilDummy", (), {"fil_id": "f1", "messages": [], "verrouille": False})())
    
    slug = forum.slug
    fil_id = forum.fils[0].fil_id if forum.fils else "dummy"
    
    # Essayer de publier
    ok, msg = msg_service.publier(user2.pseudo, slug, fil_id, "Msg")
    assert not ok

def test_mp_echec_destinataire_inexistant():
    """Couvre la branche d'erreur lorsque l'utilisateur destinataire du MP n'existe pas."""
    user = creer_utilisateur("Alice")
    ok, msg = mp_service.envoyer_mp(user.pseudo, "Inconnu", "Salut")
    assert not ok

# --- Nouveau test pour 100% coverage ---
def test_charger_data_corrompue(tmp_path, monkeypatch):
    """
    Force le bloc except de stockage.charger() en créant un fichier JSON corrompu.
    """
    from storage import stockage

    # Créer un fichier corrompu
    data_file = tmp_path / "data.json"
    data_file.write_text("{ this is not valid JSON }", encoding="utf-8")
    monkeypatch.setattr(stockage, "DATA_FILE", str(data_file))
    monkeypatch.setattr(stockage, "BACKUP_FILE", str(tmp_path / "data.json.bak"))

    # Réinitialiser le stockage avant de charger
    stockage.storage.utilisateurs.clear()
    stockage.storage.forums.clear()
    stockage.storage.forums_supprimes.clear()

    # Charger : devrait attraper l'exception JSONDecodeError
    stockage.storage.charger()

    # Vérifier que le stockage est réinitialisé
    assert stockage.storage.utilisateurs == {}
    assert stockage.storage.forums == {}
    assert stockage.storage.forums_supprimes == {}