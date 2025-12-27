from models.forum import Forum
from models.fil import Fil
from models.message import Message
from .test_extra_coverage import make_user


def test_forum_creation_noms_extremes():
    admin = make_user("Admin")
    # Test noms courts
    forum = Forum("forum1", "A", "a-slug", admin.pseudo)  # forum_id, nom, slug, createur_pseudo
    assert forum.nom == "A"
    assert forum.slug == "a-slug"
    # Test noms très longs
    long_name = "X" * 500
    forum2 = Forum("forum2", long_name, "long-slug", admin.pseudo)
    assert forum2.nom == long_name
    assert forum2.slug == "long-slug"


def test_fil_creation_titres_extremes():
    user = make_user("Alice")
    # Test titre court
    fil = Fil("fil1", "X", user.pseudo)  # fil_id, titre, createur_pseudo
    assert fil.titre == "X"
    # Test titre très long
    long_title = "T" * 500
    fil2 = Fil("fil2", long_title, user.pseudo)
    assert fil2.titre == long_title


def test_message_contenu_extreme():
    user = make_user("Bob")
    # Message vide
    msg_empty = Message("msg1", user.pseudo, "")
    assert msg_empty.texte == ""
    # Message très long
    huge_text = "hello" * 5000
    msg_big = Message("msg2", user.pseudo, huge_text)
    assert msg_big.texte == huge_text


def test_forum_rejoin_multiple_times():
    admin = make_user("Admin")
    user = make_user("Alice")
    forum = Forum("forum3", "MonForum", "monforum", admin.pseudo)
    # Rejoindre deux fois
    forum.rejoindre(user.pseudo)
    forum.rejoindre(user.pseudo)  # ne doit pas planter
    assert user.pseudo in forum.membres


def test_fil_ajout_messages_massif():
    user = make_user("Alice")
    fil = Fil("fil3", "Desc", user.pseudo)
    # Ajouter beaucoup de messages
    for i in range(2000):
        fil.messages.append(Message(f"msg{i}", user.pseudo, f"msg {i}"))
    assert len(fil.messages) == 2000


def test_message_like_dislike_extreme():
    user = make_user("Alice")
    other = make_user("Bob")
    msg = Message("msg100", user.pseudo, "test")
    # Répéter likes et dislikes
    for _ in range(500):
        msg.likes.add(other.pseudo)
        msg.dislikes.add(other.pseudo)
    # Comme sets, la longueur ne peut dépasser 1 par utilisateur
    assert len(msg.likes) == 1
    assert len(msg.dislikes) == 1


def test_forum_bannir_deja_banni():
    admin = make_user("Admin")
    user = make_user("Alice")
    forum = Forum("forum4", "ForumTest", "forumtest", admin.pseudo)
    forum.rejoindre(user.pseudo)
    forum.bannir(user.pseudo)
    # Rebannir ne doit pas planter
    forum.bannir(user.pseudo)
    assert user.pseudo in forum.bannis


def test_forum_debannir_non_banni():
    admin = make_user("Admin")
    user = make_user("Alice")
    forum = Forum("forum5", "ForumTest", "forumtest", admin.pseudo)
    # Débannir un non-banni
    forum.debannir(user.pseudo)
    assert user.pseudo not in forum.bannis


def test_message_like_par_auteur_soi_meme():
    user = make_user("Alice")
    msg = Message("msg200", user.pseudo, "self like test")
    # Self-like selon logique
    msg.likes.add(user.pseudo)
    assert user.pseudo in msg.likes


def test_message_dislike_par_auteur_soi_meme():
    user = make_user("Alice")
    msg = Message("msg201", user.pseudo, "self dislike test")
    # Self-dislike selon logique
    msg.dislikes.add(user.pseudo)
    assert user.pseudo in msg.dislikes