# tests/test_full_coverage.py
import pytest
from storage.stockage import storage
from models.utilisateur import Utilisateur
from services.auth_service import auth_service
from services.forum_service import forum_service
from services.fil_service import fil_service
from services.message_service import message_service
from services.badge_service import badge_service
from services.mp_service import mp_service
from services.search_service import search_service
from services.notification_service import notification_service


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
    ok, _ = auth_service.inscription("Alice", "pass")
    return storage.utilisateurs["Alice"]

@pytest.fixture
def user2():
    ok, _ = auth_service.inscription("Bob", "pass")
    return storage.utilisateurs["Bob"]

@pytest.fixture
def user3():
    ok, _ = auth_service.inscription("Charlie", "pass")
    return storage.utilisateurs["Charlie"]


def test_mp_envoi_reception(user, user2):
    """Test MP envoi et réception."""
    ok, msg = mp_service.envoyer_mp(user.pseudo, user2.pseudo, "Salut Bob")
    assert ok
    assert len(user2.inbox) == 1
    assert user2.inbox[0]["texte"] == "Salut Bob"
    assert len(user.outbox) == 1


def test_mp_destinataire_inexistant(user):
    """MP vers pseudo inexistant."""
    ok, msg = mp_service.envoyer_mp(user.pseudo, "Inconnu", "Hello")
    assert not ok
    assert "introuvable" in msg.lower()


def test_search_forums_fil_messages(user):
    """Recherche multi-niveaux."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumSearchFull")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilImportant")
    fil_id = storage.forums[slug].fils[0].fil_id
    message_service.publier(user.pseudo, slug, fil_id, "Contenu unique pour test")

    ok, results = search_service.rechercher("unique pour test")
    assert ok
    assert any("Contenu unique" in r["texte"] for r in results)

    ok, results = search_service.rechercher("inexistant")
    assert not ok


def test_notifications_completes(user, user2):
    """Créer et gérer plusieurs notifications."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumNotifFull")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilNotif")
    fil_id = storage.forums[slug].fils[0].fil_id

    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    for i in range(3):
        message_service.publier(user.pseudo, slug, fil_id, f"Message {i+1}")

    ok, notifs = notification_service.lister_non_lues(user.pseudo)
    assert ok
    assert len(notifs) == 3

    ok, msg = notification_service.marquer_lues(user.pseudo)
    assert ok
    ok, notifs = notification_service.lister_non_lues(user.pseudo)
    assert ok
    assert len(notifs) == 0


def test_liker_disliker_multiple(user, user2):
    """Vérifie qu'un utilisateur ne peut liker/disliker qu'une fois."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumLikesFull")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilLike")
    fil_id = storage.forums[slug].fils[0].fil_id
    message_service.publier(user.pseudo, slug, fil_id, "Msg test")
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

    # Dislike après like → doit être possible et enlever le like
    ok, msg_like = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=False)
    assert ok
    msg_obj = next(m for m in storage.forums[slug].fils[0].messages if m.msg_id == msg_id)
    assert user2.pseudo not in msg_obj.likes
    assert user2.pseudo in msg_obj.dislikes


def test_suppression_message_like_dislike(user, user2):
    """Après suppression, impossible de liker/disliker."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumDelMsgFull")
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilDel")
    fil_id = storage.forums[slug].fils[0].fil_id
    message_service.publier(user.pseudo, slug, fil_id, "Msg test")
    msg_id = storage.forums[slug].fils[0].messages[0].msg_id

    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    ok, msg_suppr = message_service.mod_supprimer_message(user.pseudo, slug, fil_id, msg_id)
    assert ok

    ok, msg_like = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=True)
    assert not ok
    assert "introuvable" in msg_like.lower()