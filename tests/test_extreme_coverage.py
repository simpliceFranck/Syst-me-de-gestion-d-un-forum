from models.forum import Forum
from .test_extra_coverage import make_user

def test_forum_bannir_et_reintegrer():
    admin = make_user("Admin")
    user = make_user("Alice")
    forum = Forum("Mon Forum", "mon-forum", "mon-forum-slug", admin.pseudo)

    forum.rejoindre(user.pseudo)
    ok, _ = forum.bannir(user.pseudo)
    assert ok
    assert user.pseudo in forum.bannis

    # réintégrer
    forum.anciens_membres.remove(user.pseudo)
    forum.membres.add(user.pseudo)
    assert user.pseudo in forum.membres