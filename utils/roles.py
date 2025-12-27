from storage.stockage import storage

def role_local(pseudo, forum_slug):
    """
    Retourne le rôle local d'un utilisateur dans un forum :
    'admin', 'modo', 'membre' ou None
    """
    user = storage.utilisateurs.get(pseudo)
    if not user:
        return None
    return user.forums_rejoints.get(forum_slug)