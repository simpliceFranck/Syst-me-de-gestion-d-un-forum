
import pytest

from storage.stockage import storage
from models.utilisateur import Utilisateur
from models.forum import Forum
from models.fil import Fil
from utils.slug import Slug
from services.notification_service import notification_service
from services.message_service import message_service


@pytest.fixture(autouse=True)
def clean_storage():
    """Réinitialise le storage avant chaque test pour garantir isolation."""
    storage.forums.clear()
    storage.utilisateurs.clear()
    storage.forums_supprimes.clear()
    yield
    storage.forums.clear()
    storage.utilisateurs.clear()
    storage.forums_supprimes.clear()

@pytest.fixture
def user():
    u = Utilisateur("U1", "TestUser", "hashpwd", "sel")
    storage.utilisateurs[u.pseudo] = u
    return u

@pytest.fixture
def other_user():
    u2 = Utilisateur("U2", "OtherUser", "hash2", "sel2")
    storage.utilisateurs[u2.pseudo] = u2
    return u2

@pytest.fixture
def forum(user):
    """Crée un forum avec le créateur user (devient admin local)."""
    slug = Slug.vers_slug("Forum Test")
    f = Forum("FORUM_1", "Forum Test", slug, user.pseudo)
    storage.forums[slug] = f
    # mettre à jour l'utilisateur localement pour refléter qu'il est admin du forum
    user.forums_crees.append(slug)
    user.forums_rejoints[slug] = "admin"
    return f

@pytest.fixture
def fil(forum, user):
    """Crée un fil dans le forum et le retourne."""
    fil_obj = Fil("FIL_1", "Sujet Principal", user.pseudo)
    forum.fils.append(fil_obj)
    return fil_obj


def test_slug_prefix_and_no_accents():
    s = Slug.vers_slug("École de l'été 2025!")
    # ta fonction produit "SL-" comme préfixe selon le code fourni
    assert s.startswith("SL-")
    # accents transformés (aucun 'é' laissé)
    assert "é" not in s.lower()
    assert " " not in s  # espaces remplacés par tirets


def test_notification_service_create_and_list_and_mark(user):
    ok, msg = notification_service.creer_notification(user.pseudo, "Hello notif")
    assert ok is True
    ok, notifs = notification_service.lister_non_lues(user.pseudo)
    assert ok is True
    assert any(n["texte"] == "Hello notif" and not n["lu"] for n in notifs)

    ok, _ = notification_service.marquer_lues(user.pseudo)
    assert ok is True
    ok, notifs2 = notification_service.lister_non_lues(user.pseudo)
    assert ok is True
    assert not notifs2  # plus de non-lues


def test_badge_attribution_after_first_message(user, forum, fil):
    # user est admin local et membre ; publier un message doit créer badge seuil=1
    ok, msg = message_service.publier(user.pseudo, forum.slug, fil.fil_id, "Bonjour tout le monde")
    assert ok is True
    # Vérifier qu'un badge "Nouveau contributeur" (config par défaut) a été attribué
    # badge_service ajoute "Nouveau contributeur" pour seuil 1
    u = storage.utilisateurs[user.pseudo]
    assert any("Nouveau" in b for b in u.badges)

    # Vérifier qu'une notification a bien été créée pour ce badge
    assert any("Nouveau badge" in n["texte"] or "Nouveau contributeur" in n["texte"] for n in u.notifications)


def test_like_triggers_premier_like_badge(user, other_user, forum, fil):
    # publier un message par user
    ok, _ = message_service.publier(user.pseudo, forum.slug, fil.fil_id, "Message à liker")
    assert ok
    msg = fil.messages[-1]

    # autre utilisateur devient membre du forum (simulate)
    other_user.forums_rejoints[forum.slug] = "membre"
    # other_user like le message
    ok, resp = message_service.liker(other_user.pseudo, forum.slug, fil.fil_id, msg.msg_id, like=True)
    assert ok is True
    # auteur (user) doit recevoir badge 'premier_like' via badge_evenement -> "Apprécié"
    u = storage.utilisateurs[user.pseudo]
    assert any("Apprécié" in b or "Apprécié" == b for b in u.badges) or any("Apprécié" in n["texte"] for n in u.notifications)


def test_like_disallow_duplicate(user, other_user, forum, fil):
    ok, _ = message_service.publier(user.pseudo, forum.slug, fil.fil_id, "Message X")
    msg = fil.messages[-1]
    other_user.forums_rejoints[forum.slug] = "membre"

    ok, _ = message_service.liker(other_user.pseudo, forum.slug, fil.fil_id, msg.msg_id, like=True)
    assert ok is True

    # essayer de liker à nouveau -> doit échouer
    ok2, m2 = message_service.liker(other_user.pseudo, forum.slug, fil.fil_id, msg.msg_id, like=True)
    assert ok2 is False
    assert "déjà liké" in m2.lower()


def test_modifier_message_by_author(user, forum, fil):
    ok, _ = message_service.publier(user.pseudo, forum.slug, fil.fil_id, "Texte initial")
    assert ok
    msg = fil.messages[-1]
    ok, resp = message_service.modifier(user.pseudo, forum.slug, fil.fil_id, msg.msg_id, "Texte modifié")
    assert ok is True
    assert msg.texte == "Texte modifié"


def test_modifier_message_forbidden_for_other(user, other_user, forum, fil):
    ok, _ = message_service.publier(user.pseudo, forum.slug, fil.fil_id, "Texte initial")
    msg = fil.messages[-1]
    # other_user n'est pas membre -> ne peut modifier
    ok, resp = message_service.modifier(other_user.pseudo, forum.slug, fil.fil_id, msg.msg_id, "Malicious")
    assert ok is False
    assert "permission" in resp.lower() or "autorisé" in resp.lower()


def test_mod_supprimer_message_by_admin(user, other_user, forum, fil):
    # publier un message par other_user (faire en sorte qu'il soit membre)
    other_user.forums_rejoints[forum.slug] = "membre"
    ok, _ = message_service.publier(other_user.pseudo, forum.slug, fil.fil_id, "Message supprimable")
    msg = fil.messages[-1]
    # user (admin local) supprime le message
    ok, resp = message_service.mod_supprimer_message(user.pseudo, forum.slug, fil.fil_id, msg.msg_id)
    assert ok is True
    assert all(m.msg_id != msg.msg_id for m in fil.messages)


def test_forum_verrouille_blocks_member_publish(user, other_user, forum, fil):
    # rendre forum verrouillé
    ok, _ = forum.verrouiller()
    assert ok is True
    # other_user est membre -> mais lorsqu'il tente de publier, il doit être bloqué
    other_user.forums_rejoints[forum.slug] = "membre"
    ok, resp = message_service.publier(other_user.pseudo, forum.slug, fil.fil_id, "Tentative")
    assert ok is False
    assert "verrouillé" in resp.lower()

    # admin (user) peut toujours publier
    ok_admin, _ = message_service.publier(user.pseudo, forum.slug, fil.fil_id, "Admin poste")
    assert ok_admin is True


def test_bannir_deplace_roles_and_blocks(member=None, user=None):
    # This test uses manual creation because of signature constraints in parameterization
    # We'll create a forum and a member, then ban that member
    u = Utilisateur("U10", "BanGuy", "h", "s")
    storage.utilisateurs[u.pseudo] = u
    slug = Slug.vers_slug("ForumBan")
    f = Forum("FORUM_BAN", "ForumBan", slug, "TestUser")
    storage.forums[slug] = f
    # add member
    f.rejoindre(u.pseudo)
    # ban
    ok, resp = f.bannir(u.pseudo)
    assert ok is True
    assert u.pseudo in f.bannis
    # user forums_rejoints should have been removed if present (the method already handles storage)
    assert f.slug not in u.forums_rejoints