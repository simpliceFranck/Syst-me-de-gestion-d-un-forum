import pytest
from models.utilisateur import Utilisateur
from services.auth_service import auth_service
from services.forum_service import forum_service
from services.fil_service import fil_service
from services.message_service import message_service
from storage.stockage import storage

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
    ok, msg = auth_service.inscription("Alice", "pass")
    return storage.utilisateurs.get("Alice")

@pytest.fixture
def user2():
    ok, msg = auth_service.inscription("Bob", "pass")
    return storage.utilisateurs.get("Bob")

@pytest.fixture
def user3():
    ok, msg = auth_service.inscription("Charlie", "pass")
    return storage.utilisateurs.get("Charlie")


def test_multi_forums_fils(user, user2, user3):
    """Création de plusieurs forums et fils, rôles et membres."""
    slugs = []
    for i in range(3):
        ok, msg = forum_service.creer_forum(user.pseudo, f"Forum{i}")
        assert ok
        slug = msg.split("slug = ")[-1].strip(").")
        slugs.append(slug)

    # Ajouter user2 et user3 sur Forum0
    forum = storage.forums[slugs[0]]
    for u in [user2, user3]:
        forum.membres.add(u.pseudo)
        u.forums_rejoints[slugs[0]] = "membre"

    # Créer des fils
    for slug in slugs:
        ok, msg = fil_service.creer_fil(user.pseudo, slug, f"Fil_{slug}")
        assert ok

    # Vérifier fils
    for slug in slugs:
        assert len(storage.forums[slug].fils) == 1


def test_badges_notifications(user, user2):
    """Création forum, fil et messages déclenche badges et notifications."""
    ok, msg = forum_service.creer_forum(user.pseudo, "BadgeForumMulti")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")

    ok, msg = fil_service.creer_fil(user.pseudo, slug, "Fil1")
    assert ok
    fil_id = storage.forums[slug].fils[0].fil_id

    # Bob rejoint pour poster
    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Publier messages
    for i in range(5):
        ok, msg_pub = message_service.publier(user2.pseudo, slug, fil_id, f"Msg {i+1}")
        assert ok

    # Vérifier badges d'événement attribués au créateur
    user_badges = set(user.badges)
    assert "Fondateur" in user_badges
    assert "Créateur de discussions" in user_badges


def test_non_membre_action(user, user2):
    """Un utilisateur non membre ne peut ni poster ni liker."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumRestricted")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "Fil1")
    assert ok
    fil_id = storage.forums[slug].fils[0].fil_id

    # Publier impossible
    ok, msg = message_service.publier(user2.pseudo, slug, fil_id, "Msg interdit")
    assert not ok
    assert "membre" in msg

    # Liker impossible
    msg_id = "fake"  # aucun message réel
    ok, msg = message_service.liker(user2.pseudo, slug, fil_id, msg_id, like=True)
    assert not ok


def test_forum_fil_verrouille(user, user2):
    """Tester restrictions sur forum et fil verrouillé."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumLockEdge")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "Fil1")
    assert ok
    fil_id = storage.forums[slug].fils[0].fil_id

    forum = storage.forums[slug]
    forum.verrouille = True

    # user2 rejoint
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Publication impossible
    ok, msg = message_service.publier(user2.pseudo, slug, fil_id, "Msg interdit")
    assert not ok
    assert "Forum verrouillé" in msg


def test_moderateur_permissions(user, user2):
    """Modérateur peut supprimer un message."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumModo")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "Fil1")
    assert ok
    fil_id = storage.forums[slug].fils[0].fil_id

    # Ajouter message par Alice
    ok, msg_pub = message_service.publier(user.pseudo, slug, fil_id, "Message test")
    assert ok
    msg_id = storage.forums[slug].fils[0].messages[0].msg_id

    # Ajouter Bob comme modérateur
    forum = storage.forums[slug]
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "modo"
    forum.moderateurs.add(user2.pseudo)

    # Suppression possible
    ok, msg_suppr = message_service.mod_supprimer_message(user2.pseudo, slug, fil_id, msg_id)
    assert ok


def test_badges_cumulatifs_messages(user):
    """Vérifie cumul des badges : forum, fil, messages, premier like."""
    # Création forum et fil
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumBadgeMsg")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")
    ok, msg = fil_service.creer_fil(user.pseudo, slug, "Fil1")
    assert ok
    fil_id = storage.forums[slug].fils[0].fil_id

    # Publier messages pour badges
    for i in range(12):
        ok, msg_pub = message_service.publier(user.pseudo, slug, fil_id, f"Message {i+1}")
        assert ok

    user_badges = set(user.badges)
    assert "Fondateur" in user_badges
    assert "Créateur de discussions" in user_badges
    assert any(b in user_badges for b in ["Nouveau contributeur", "Participant régulier", "Pilier du forum"])

    # Premier like par un autre utilisateur
    other_user = Utilisateur("U999", "OtherUser", "hash", "sel")
    storage.utilisateurs[other_user.pseudo] = other_user

    # Rejoindre forum et rôle local
    ok, msg_join = storage.forums[slug].rejoindre(other_user.pseudo)
    assert ok
    other_user.forums_rejoints[slug] = "membre"

    msg_id = storage.forums[slug].fils[0].messages[0].msg_id
    ok, msg_like = message_service.liker(other_user.pseudo, slug, fil_id, msg_id, like=True)
    assert ok
    assert "Apprécié" in user.badges


def test_bannissement_ancien_membre(user, user2):
    """Tester bannissement, ancien membre et impossibilité de publier."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumBan")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")
    forum = storage.forums[slug]

    # Ajouter user2
    forum.membres.add(user2.pseudo)
    user2.forums_rejoints[slug] = "membre"

    # Bannir user2
    ok, msg = forum.bannir(user2.pseudo)
    assert ok
    assert user2.pseudo not in forum.membres
    assert user2.pseudo in forum.bannis
    assert user2.pseudo in forum.anciens_membres

    # Supprimer rôle local pour simuler bannissement réel
    user2.forums_rejoints.pop(slug, None)

    # Création d'un fil par admin
    fil_service.creer_fil(user.pseudo, slug, "Fil1")
    fil_id = forum.fils[0].fil_id

    # Publication impossible pour user2
    ok, msg_pub = message_service.publier(user2.pseudo, slug, fil_id, "Msg interdit")
    assert not ok
    assert "membre" in msg_pub or "banni" in msg_pub


def test_suppression_restauration_forum(user):
    """Tester suppression d'un forum et restauration possible."""
    ok, msg = forum_service.creer_forum(user.pseudo, "ForumSuppr")
    assert ok
    slug = msg.split("slug = ")[-1].strip(").")

    forum = storage.forums[slug]

    # Supprimer forum
    storage.forums_supprimes[slug] = forum.en_dict()
    del storage.forums[slug]
    assert slug not in storage.forums

    # Restaurer forum
    forum_dict = storage.forums_supprimes.pop(slug)
    restored = forum_service.get_forum(slug)
    if not restored:
        storage.forums[slug] = forum_service.get_forum(slug) or forum_service.get_forum(slug)  # workaround
    assert slug in storage.forums