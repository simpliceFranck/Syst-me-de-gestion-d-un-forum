import pytest
from models.utilisateur import Utilisateur
from services.mp_service import mp_service
from services.search_service import search_service
from services.notification_service import notification_service
from services.forum_service import forum_service
from services.fil_service import fil_service
from services.message_service import message_service
from storage.stockage import storage

# --- Fixtures ---
@pytest.fixture(scope="function", autouse=True)
def clear_storage():
    """Réinitialise le stockage avant chaque test."""
    storage.utilisateurs.clear()
    storage.forums.clear()
    storage.forums_supprimes.clear()
    yield
    storage.utilisateurs.clear()
    storage.forums.clear()
    storage.forums_supprimes.clear()

@pytest.fixture
def user():
    u = Utilisateur("U1", "User1", "hash", "sel")
    storage.utilisateurs[u.pseudo] = u
    return u

@pytest.fixture
def user2():
    u = Utilisateur("U2", "User2", "hash", "sel")
    storage.utilisateurs[u.pseudo] = u
    return u

# --- Tests MP Service ---
def test_mp_service_basic(user, user2):
    """Envoi et réception de messages privés"""
    ok, msg = mp_service.envoyer_mp(user.pseudo, user2.pseudo, "Bonjour Bob")
    assert ok
    assert len(user2.inbox) == 1
    assert user2.inbox[0]["texte"] == "Bonjour Bob"

def test_mp_service_nonexistent_recipient(user):
    """Tentative d'envoi à un pseudo inexistant"""
    ok, msg = mp_service.envoyer_mp(user.pseudo, "Inconnu", "Hello")
    assert not ok
    assert "introuvable" in msg

def test_mp_service_boites(user, user2):
    """Vérification des boîtes envoyés/reçus"""
    mp_service.envoyer_mp(user.pseudo, user2.pseudo, "Msg1")
    mp_service.envoyer_mp(user.pseudo, user2.pseudo, "Msg2")
    assert len(user2.inbox) == 2
    assert len(user.outbox) == 2

# --- Tests Search Service ---
def test_search_forum_fil_message(user, user2):
    """Recherche multi-niveaux (forums, fils, messages)"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumSearch")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilImportant")
    fil_id = storage.forums[slug].fils[0].fil_id
    message_service.publier(user.pseudo, slug, fil_id, "Contenu unique pour test")

    ok, results = search_service.rechercher("unique pour test")
    assert ok
    assert any(r["texte"] == "Contenu unique pour test" for r in results)

def test_search_not_found(user):
    """Recherche avec aucun résultat"""
    ok, results = search_service.rechercher("Inexistant")
    assert not ok
    assert results == "Aucun résultat."

# --- Tests Notification Service ---
def test_notifications_multiple(user, user2):
    """Création de plusieurs notifications et marquage partiel/total"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumNotifMulti")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilNotif")
    fil_id = storage.forums[slug].fils[0].fil_id

    # Ajouter user2
    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Publier plusieurs messages → notifications au créateur
    for i in range(3):
        message_service.publier(user.pseudo, slug, fil_id, f"Message {i+1}")

    # Lister notifications non lues
    ok, notifs = notification_service.lister_non_lues(user.pseudo)
    assert ok
    assert len(notifs) > 0

    # Marquer toutes lues
    ok, msg = notification_service.marquer_lues(user.pseudo)
    assert ok
    ok, notifs = notification_service.lister_non_lues(user.pseudo)
    assert ok
    assert len(notifs) == 0

# --- Tests Like/Dislike ---
def test_like_dislike_multiple(user, user2):
    """Un utilisateur ne peut liker/disliker plusieurs fois le même message"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumLikes")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilLike")
    fil_id = storage.forums[slug].fils[0].fil_id
    ok, msg_pub = message_service.publier(user.pseudo, slug, fil_id, "Msg test")
    msg_id = storage.forums[slug].fils[0].messages[0].msg_id

    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Premier like
    ok, msg_like = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=True)
    assert ok

    # Essai de liker à nouveau → doit échouer
    ok, msg_like = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=True)
    assert not ok

# --- Test suppression message ---
def test_suppression_message(user, user2):
    """Après suppression, impossible de liker/disliker le message"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumDelMsg")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilDel")
    fil_id = storage.forums[slug].fils[0].fil_id
    ok, msg_pub = message_service.publier(user.pseudo, slug, fil_id, "Msg test")
    msg_id = storage.forums[slug].fils[0].messages[0].msg_id

    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Supprimer message
    ok, msg_suppr = message_service.mod_supprimer_message(user.pseudo, slug, fil_id, msg_id)
    assert ok

    # Tentative de like → échoue
    ok, msg_like = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=True)
    assert not ok
    assert "introuvable" in msg_like.lower()