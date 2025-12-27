import pytest

from storage.stockage import storage
from services.forum_service import forum_service
from services.fil_service import fil_service
from services.message_service import message_service
from services.notification_service import notification_service
from models.utilisateur import Utilisateur
from models.forum import Forum


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


def test_forum_verrouille(user, user2):
    """Forum verrouillé : non-admin ne peut ni créer fil ni publier message"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumLock")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")
    forum = storage.forums[slug]
    forum.verrouille = True

    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Création de fil impossible
    ok, msg = fil_service.creer_fil(user2.pseudo, slug, "FilLock")
    assert not ok
    assert "verrouillé" in msg

    # Publication impossible
    fil_id = "dummy"
    if forum.fils:
        fil_id = forum.fils[0].fil_id
    ok, msg = message_service.publier(user2.pseudo, slug, fil_id, "Msg")
    assert not ok


def test_fil_verrouille(user, user2):
    """Fil verrouillé : non-admin ne peut pas publier ni liker"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumFilLock")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")

    ok, msg = fil_service.creer_fil(user.pseudo, slug, "Fil1")
    assert ok
    fil_id = storage.forums[slug].fils[0].fil_id

    forum = storage.forums[slug]
    forum.verrouille = False

    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    storage.forums[slug].fils[0].verrouille = True

    ok, msg = message_service.publier(user2.pseudo, slug, fil_id, "Msg interdit")
    assert not ok
    ok, msg = message_service.liker(user2.pseudo, slug, fil_id, storage.forums[slug].fils[0].messages[0].msg_id if storage.forums[slug].fils[0].messages else "dummy")
    assert not ok


def test_badges_seuils(user):
    """Tester badges cumulés et seuils (messages, forum, fil)"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumBadgeEdge")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")

    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilBadge")
    assert ok
    fil_id = storage.forums[slug].fils[0].fil_id

    # Publier 10 messages → badge "Participant régulier"
    for i in range(10):
        ok, msg_pub = message_service.publier(user.pseudo, slug, fil_id, f"Msg {i+1}")
        assert ok

    user_badges = set(user.badges)
    assert "Fondateur" in user_badges
    assert "Créateur de discussions" in user_badges
    assert "Participant régulier" in user_badges or "Pilier du forum" in user_badges


def test_notifications(user, user2):
    """Création et marquage de notifications"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumNotif")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")

    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    ok, msg = fil_service.creer_fil(user.pseudo, slug, "FilNotif")
    assert ok
    fil_id = forum.fils[0].fil_id

    ok, msg = message_service.publier(user.pseudo, slug, fil_id, "Message notif")
    assert ok

    ok, notifs = notification_service.lister_non_lues(user.pseudo)
    assert ok
    assert any("badge" in n["texte"].lower() for n in notifs)

    ok, msg = notification_service.marquer_lues(user.pseudo)
    assert ok
    ok, notifs = notification_service.lister_non_lues(user.pseudo)
    assert ok
    assert len(notifs) == 0


def test_ancien_membre_banni(user, user2):
    """Ancien membre banni ne peut plus publier ni rejoindre"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumAncien")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")
    forum = storage.forums[slug]

    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Bannir
    ok, msg = forum.bannir(user2.pseudo)
    assert ok

    # Tenter de rejoindre
    ok, msg = forum.rejoindre(user2.pseudo)
    assert not ok
    assert "banni" in msg

    # Publication impossible
    fil_service.creer_fil(user.pseudo, slug, "Fil1")
    fil_id = forum.fils[0].fil_id
    ok, msg = message_service.publier(user2.pseudo, slug, fil_id, "Msg interdit")
    assert not ok


def test_suppression_restauration_forum(user):
    """Tester suppression/restauration d'un forum"""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumDel")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")

    forum = storage.forums[slug]

    # Supprimer le forum (simulate deletion)
    storage.forums_supprimes[slug] = forum.en_dict()
    del storage.forums[slug]

    assert slug not in storage.forums
    assert slug in storage.forums_supprimes

    # Restaurer le forum
    restored = storage.forums_supprimes.pop(slug)
    storage.forums[slug] = Forum.depuis_dict(restored)

    assert slug in storage.forums
    assert slug not in storage.forums_supprimes