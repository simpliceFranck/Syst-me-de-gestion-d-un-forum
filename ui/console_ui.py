from getpass import getpass
from textwrap import dedent

from utils.couleurs import couleur, Couleurs
from services.auth_service import auth_service
from storage.stockage import storage
from services.notification_service import notification_service

def afficher_notifications(user):
    ok, non_lues = notification_service.lister_non_lues(user.pseudo)
    # 1. Gestion plus robuste des erreurs : distinguer les cas
    if not ok:
        couleur.print_rouge("[ERREUR] Impossible de récupérer les notifications.")
        return
    # 2. Distinguer entre "aucune notification" et valeur None
    if non_lues is None:
        couleur.print_rouge("[ERREUR] Données de notifications invalides.")
        return
    if len(non_lues) == 0:
        couleur.print_vert("Aucune notification non lue.")
        return
    m = len(non_lues)
    titre = "Notifications non lues" if m >= 2 else "Notification non lue"
    couleur.print_vert(f"{m} {titre} :")
    # 3. Accès sécurisé au texte des notifications
    for i, n in enumerate(non_lues, 1):
        texte = n.get("texte", "(Notification sans texte)")
        if m == 1:
            couleur.print_vert(texte)
        else:
            couleur.print_vert(f"{i} - {texte}")

def afficher_mes_forums(user):
    forums = user.forums_rejoints
    # Aucun forum
    if not forums:
        couleur.print_jaune("Vous n'êtes membre d'aucun forum.")
        return
    # Plusieurs forums (ou un seul)
    for i, (slug, role) in enumerate(forums.items(), 1):
        f = storage.forums.get(slug)
        if f:
            print(f"{i} - {f.nom} (slug = {slug}) [{role}]")
        else:
            # Forum introuvable dans le storage
            print(f"{i} - Forum inconnu (slug = {slug}) [{role}]")

def afficher_inbox(user, marquer_comme_lu=True):
    inbox = getattr(user, "inbox", None) # essaie d’obtenir la valeur de l’attribut inbox, sinon None.
    if not isinstance(inbox, list) or not inbox:
        couleur.print_jaune("Inbox vide")
        return
    for i, mp in enumerate(inbox, 1):
        if not isinstance(mp, dict):
            print(f"{i} - Message corrompu, ignoré.")
            continue
        de = mp.get("de", "Expéditeur inconnu")
        texte = mp.get("texte", "(Message vide)")
        lu = bool(mp.get("lu", False))
        statut = (f"{couleur.VERT}Lu{couleur.RESET}"
                  if lu else
                  f"{couleur.ROUGE}Non lu{couleur.RESET}")
        print(dedent(f"""
            {i} - De {de} :
            {statut}
            {texte}
        """))
        if not lu and marquer_comme_lu:
            mp["lu"] = True
    try:
        storage.sauvegarder()
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

def afficher_forum(forum):
    """Affiche toutes les informations d'un forum et ses fils de discussion."""
    def afficher_infos_forum(forum):
        """Affiche les informations générales du forum."""
        print(dedent(f"""
        Nom : {forum.nom}
        Slug : {forum.slug}
        Admin : {forum.admin}
        Verrouillé : {"Oui" if forum.verrouille else "Non"}
        Modérateurs : {", ".join(forum.moderateurs) or "Aucun"}
        Membres : {", ".join(forum.membres) or "Aucun"}
        Bannis : {", ".join(forum.bannis) or "Aucun"}
        Anciens membres : {", ".join(forum.anciens_membres) or "Aucun"}"""))
    def afficher_messages(messages):
        """Affiche la liste des messages d'un fil."""
        if not messages:
            print("Aucun message.")
            return
        couleur.print_vert("Messages :")
        for i, msg in enumerate(messages, 1):
            likes = set(getattr(msg, "likes", []))
            dislikes = set(getattr(msg, "dislikes", []))
            print(dedent(f"""\ 
            {i} - {msg.auteur_pseudo} (ID = {msg.msg_id}):
            {msg.texte} 
            👍{len(likes)} 👎{len(dislikes)}"""))
    def afficher_fils(fils):
        """Affiche les fils de discussion du forum."""
        if not fils:
            couleur.print_jaune("\nAucun fil de discussion.")
            return
        for i, fil in enumerate(fils, 1):
            verrou = f"{Couleurs.Rouge}Fil fermé{Couleurs.RESET}" if fil.verrouille else f"{Couleurs.VERT}Fil ouvert{Couleurs.RESET}"
            couleur.print_bleu(f"\nFil {i} : {fil.titre} (ID = {fil.fil_id}) [{verrou}]")
            afficher_messages(fil.messages)
    # --- Execution ---
    afficher_infos_forum(forum)
    afficher_fils(forum.fils)

# def afficher_forum(forum):
#     # Informations du forum
#     print(dedent(f"""
#     Nom : {forum.nom}
#     Slug : {forum.slug}
#     Admin : {forum.admin}
#     Verrouillé : {"Oui" if forum.verrouille else "Non"}
#     Modérateurs : {", ".join(forum.moderateurs) or "Aucun"}
#     Membres : {", ".join(forum.membres) or "Aucun"}
#     Bannis : {", ".join(forum.bannis) or "Aucun"}
#     Anciens membres : {", ".join(forum.anciens_membres) or "Aucun"}"""))
#     if not forum.fils:
#         couleur.print_jaune("\nAucun fil de discussion.")
#         return
#     # Fils de discussion
#     for i, fil in enumerate(forum.fils, 1):
#         verrou = f"{Couleurs.Rouge}Fil fermé{Couleurs.RESET}" if fil.verrouille else f"{Couleurs.VERT}Fil ouvert{Couleurs.RESET}"
#         couleur.print_bleu(f"\nFil {i} : {fil.titre} (ID = {fil.fil_id}) [{verrou}]")
#         if not fil.messages:
#             print("Aucun message.")
#             continue
#         couleur.print_vert("Messages :")
#         for x, msg in enumerate(fil.messages, 1):
#             likes = set(getattr(msg, "likes", []))
#             dislikes = set(getattr(msg, "dislikes", []))
#             print(dedent(f"""\ 
#             {x} - {msg.auteur_pseudo} (ID = {msg.msg_id}):
#             {msg.texte} 
#             👍{len(likes)} 👎{len(dislikes)}"""))

def page_inscription():
    couleur.print_cyan("\n==== Inscription ====")
    while True:
        pseudo = input("Choisis un pseudo : ").strip()
        if not pseudo:
            couleur.print_rouge("Le pseudo ne peut pas être vide.")
            continue
        mdp = getpass("Choisis un mot de passe : ").strip()
        if len(mdp) < 6:
            couleur.print_rouge("Le mot de passe doit contenir au moins 6 caractères.")
            continue
        ok, msg = auth_service.inscription(pseudo, mdp)
        couleur.print_jaune(msg)
        if ok:
            utilisateur = storage.utilisateurs.get(pseudo)
            if utilisateur:
                return utilisateur
            else:
                couleur.print_rouge("Erreur interne : utilisateur introuvable après inscription.")
                return None
        else:
            retry = input("Voulez-vous réessayer ? (o/n) : ").lower()
            if retry != 'o':
                return None

# def page_inscription():
#     couleur.print_cyan("\n==== Inscription ====")
#     pseudo = input("Choisis un pseudo : ").strip()
#     mdp = input("Choisis un mot de passe : ").strip()
#     ok, msg = auth_service.inscription(pseudo, mdp)
#     couleur.print_jaune(msg)
#     if ok:
#         return storage.utilisateurs.get(pseudo)
#     return None

def page_connexion():
    couleur.print_cyan("\n==== Connexion ====")
    
    pseudo = input("Pseudo : ").strip()
    if not pseudo:
        couleur.print_rouge("Pseudo requis !")
        return None
    
    mdp = getpass("Mot de passe : ").strip()
    if not mdp:
        couleur.print_rouge("Mot de passe requis !")
        return None

    try:
        ok, msg = auth_service.connexion(pseudo, mdp)
    except Exception as e:
        couleur.print_rouge(f"Erreur lors de la connexion : {e}")
        return None

    couleur.print_jaune(msg)
    
    if ok:
        user = storage.utilisateurs.get(pseudo)
        if user:
            afficher_notifications(user)
            notification_service.marquer_lues(pseudo)
            return user
        else:
            couleur.print_rouge("Utilisateur non trouvé dans le stockage.")
            return None
    return None
# def page_connexion():
#     couleur.print_cyan("\n==== Connexion ====")
#     pseudo = input("Pseudo : ").strip()
#     mdp = input("Mot de passe : ").strip()
#     ok, msg = auth_service.connexion(pseudo, mdp)
#     couleur.print_jaune(msg)
#     if ok:
#         user = storage.utilisateurs.get(pseudo)
#         afficher_notifications(user)
#         notification_service.marquer_lues(pseudo)
#         return user
#     return None