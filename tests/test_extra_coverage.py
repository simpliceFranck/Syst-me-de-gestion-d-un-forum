import pytest
from models.utilisateur import Utilisateur
from models.forum import Forum
from models.fil import Fil
from models.message import Message


def make_user(pseudo, user_id=None):
    """Crée un utilisateur pour les tests."""
    if user_id is None:
        user_id = hash(pseudo) % 10000

    return Utilisateur(
        user_id=user_id,
        pseudo=pseudo,
        mdp_hash="hash_test",
        sel="sel_test"
    )


def test_forum_bannir_et_reintegrer():
    admin = make_user("Admin")
    user = make_user("Alice")

    forum = Forum(1, "Mon Forum", "mon-forum", admin.pseudo)

    # Admin et Alice deviennent membres
    forum.membres.add(admin.pseudo)
    forum.membres.add(user.pseudo)

    # Bannissement
    ok, msg = forum.bannir(user.pseudo)
    assert ok
    assert user.pseudo in forum.bannis

    # Rejoint impossible (banni)
    ok, msg = forum.rejoindre(user.pseudo)
    assert not ok


def test_fil_messages_multiple():
    user = make_user("Alice")

    fil = Fil(100, "Titre test", user.pseudo)

    # Ajout de messages
    m1 = Message(1, user.pseudo, "Premier")
    m2 = Message(2, user.pseudo, "Deuxième")
    m3 = Message(3, user.pseudo, "Troisième")

    fil.messages.append(m1)
    fil.messages.append(m2)
    fil.messages.append(m3)

    # Vérification ordre
    assert [m.texte for m in fil.messages] == ["Premier", "Deuxième", "Troisième"]


def test_badge_evenement_multiple():
    user = make_user("Alice")

    user.badges.append("badge1")
    user.badges.append("badge2")

    assert "badge1" in user.badges
    assert "badge2" in user.badges
    assert len(user.badges) == 2


def test_message_liker_et_disliker():
    user = make_user("Alice")
    autre = make_user("Bob")

    msg = Message(1, user.pseudo, "Hello")

    msg.likes.add(autre.pseudo)
    msg.dislikes.add(user.pseudo)

    assert autre.pseudo in msg.likes
    assert user.pseudo in msg.dislikes


def test_bannissement_utilisateur_forum():
    admin = make_user("Admin")
    user = make_user("Alice")

    forum = Forum(2, "Test Forum", "test-forum", admin.pseudo)

    forum.membres.add(user.pseudo)
    assert user.pseudo in forum.membres

    ok, msg = forum.bannir(user.pseudo)
    assert ok
    assert user.pseudo in forum.bannis
    assert user.pseudo not in forum.membres