import pytest

from models.utilisateur import Utilisateur
from services.mp_service import mp_service
from services.search_service import search_service
from services.notification_service import notification_service
from services.forum_service import forum_service
from services.fil_service import fil_service
from services.message_service import message_service
from storage.stockage import storage


@pytest.fixture
def user():
    u = Utilisateur("U100", "User100", "hash", "sel")
    storage.utilisateurs[u.pseudo] = u
    return u


@pytest.fixture
def user2():
    u = Utilisateur("U200", "User200", "hash", "sel")
    storage.utilisateurs[u.pseudo] = u
    return u


def test_mp_service_errors(user):
    """Test des erreurs dans l'envoi de MP"""
    # Destinataire inexistant
    ok, msg = mp_service.envoyer_mp(user.pseudo, "Inconnu", "Hello")
    assert not ok
    assert "introuvable" in msg

    # Expéditeur inexistant (ne bloque pas l'envoi mais n'ajoute pas à outbox)
    ok, msg = mp_service.envoyer_mp("FakeUser", user.pseudo, "Hello")
    assert ok
    dest = storage.utilisateurs[user.pseudo]
    assert dest.inbox[-1]["texte"] == "Hello"


def test_search_service_edge_cases(user):
    """Recherche texte vide ou sans résultat"""
    ok, results = search_service.rechercher("   ")
    assert not ok
    assert "vide" in results

    ok, results = search_service.rechercher("Inexistant")
    assert not ok
    assert "Aucun résultat" in results


def test_notification_service_errors(user):
    """Notification pour utilisateur introuvable"""
    ok, notifs = notification_service.lister_non_lues("Inconnu")
    assert not ok
    assert notifs == []

    ok, msg = notification_service.marquer_lues("Inconnu")
    assert not ok
    assert "introuvable" in msg


def test_liker_disliker_inverse(user, user2):
    """Tester un dislike suivi d'un like pour un même message"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumLikes2")
    slug = msg.split("slug = ")[-1].strip(").")
    fil_service.creer_fil(user.pseudo, slug, "Fil1")
    fil_id = storage.forums[slug].fils[0].fil_id
    message_service.publier(user.pseudo, slug, fil_id, "Message test")
    msg_id = storage.forums[slug].fils[0].messages[0].msg_id

    # user2 rejoint
    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Dislike puis like
    ok, msg_like = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=False)
    assert ok
    ok, msg_like = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=True)
    assert ok

    msg_obj = storage.forums[slug].fils[0].messages[0]
    assert user2.pseudo in msg_obj.likes
    assert user2.pseudo not in msg_obj.dislikes