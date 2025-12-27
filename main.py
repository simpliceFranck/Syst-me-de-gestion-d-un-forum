from textwrap import dedent

from utils.couleurs import couleur
from storage.stockage import storage
from services.forum_service import forum_service
from services.fil_service import fil_service
from services.message_service import message_service
from services.mp_service import mp_service
from services.search_service import search_service
from ui.console_ui import afficher_forum, afficher_inbox, page_connexion, page_inscription, afficher_mes_forums
from models.forum import Forum

def menu_utilisateur(user):
    while True:
        couleur.print_cyan(f"\n==== MENU : {user.pseudo} ====")
        print(dedent("""\
            1. Lister les forums
            2. Rejoindre un forum
            3. Quitter un forum
            4. Voir mes forums
            5. Voir un forum
            6. Créer un forum
            7. Créer un fil
            8. Publier un message
            9. Liker / Disliker
            10. Lire notifications
            11. Lire inbox
            12. Envoyer MP
            13. Rechercher texte
            14. Modifier un message
            0. Déconnexion
        """))
        choix = input("Choix : ").strip()
        if choix == "0":
            return None
        elif choix == "1":
            ok, msg = forum_service.lister_forums()
            if not ok:
                couleur.print_jaune(msg)
            else:
                print(msg)
        elif choix == "2":
            slug = input("Slug : ").strip()
            forum = storage.forums.get(slug)
            if not forum:
                couleur.print_jaune("Forum introuvable.")
            else:
                ok, msg = forum.rejoindre(user.pseudo)
                couleur.print_jaune(msg)
                if ok:
                    user.forums_rejoints[slug] = "membre"
                    storage.sauvegarder()
        elif choix == "3":
            slug = input("Slug : ").strip()
            forum = storage.forums.get(slug)
            if not forum:
                couleur.print_jaune("Forum introuvable.")
            else:
                ok, msg = forum.quitter(user.pseudo)
                couleur.print_jaune(msg)
                if ok:
                    user.forums_rejoints.pop(slug, None)
                    storage.sauvegarder()
        elif choix == "4":
            afficher_mes_forums(user)
        elif choix == "5":
            slug = input("Slug : ").strip()
            forum = storage.forums.get(slug)
            if forum:
                afficher_forum(forum)
            else:
                couleur.print_jaune("Forum introuvable.")
        elif choix == "6":
            nom = input("Nom du forum : ").strip()
            ok, msg = forum_service.creer_forum(user.pseudo, nom)
            couleur.print_jaune(msg)
        elif choix == "7":
            slug = input("Forum slug : ").strip()
            titre = input("Titre du fil : ").strip()
            ok, msg = fil_service.creer_fil(user.pseudo, slug, titre)
            couleur.print_jaune(msg)
        elif choix == "8":
            slug = input("Forum slug : ").strip()
            fil_id = input("Fil ID : ").strip()
            texte = input("Message : ").strip()
            ok, msg = message_service.publier(user.pseudo, slug, fil_id, texte)
            couleur.print_jaune(msg)
        elif choix == "9":
            slug = input("Forum slug : ").strip()
            fil_id = input("Fil ID : ").strip()
            msg_id = input("Message ID : ").strip()
            like = input("Like ou Dislike ? (l/d) : ").strip().lower() == "l"
            ok, msg = message_service.liker(user.pseudo, slug, fil_id, msg_id, like)
            couleur.print_jaune(msg)
        elif choix == "10":
            from services.notification_service import notification_service
            ok, non_lues = notification_service.lister_non_lues(user.pseudo)
            if ok and non_lues:
                for n in non_lues:
                    couleur.print_vert(n["texte"])
                notification_service.marquer_lues(user.pseudo)
            else:
                couleur.print_vert("Aucune notification non lue.")
        elif choix == "11":
            afficher_inbox(user)
        elif choix == "12":
            cible = input("À : ").strip()
            texte = input("Texte : ").strip()
            ok, msg = mp_service.envoyer_mp(user.pseudo, cible, texte)
            if ok:
                couleur.print_vert(msg)
            else:
                couleur.print_rouge(msg)
        elif choix == "13":
            texte = input("Texte recherché : ").strip()
            ok, resultats = search_service.rechercher(texte)
            if not ok:
                couleur.print_jaune(resultats)
            else:
                for r in resultats:
                    print(f"[{r['forum']}] {r['fil']} — {r['auteur']}: {r['texte']}")
        elif choix == "14":
            slug = input("Forum slug : ").strip()
            fil_id = input("ID du fil : ").strip()
            msg_id = input("ID du message à modifier : ").strip()
            nouveau = input("Nouveau texte : ").strip()
            ok, msg = message_service.modifier(user.pseudo, slug, fil_id, msg_id, nouveau)
            couleur.print_jaune(msg)
        elif choix == "b":
            slug = input("Forum slug : ").strip()
            cible = input("Pseudo cible : ").strip()
            forum = storage.forums.get(slug)
            if not forum:
                couleur.print_jaune(f"Forum introuvable.")
            else:
                role_local = user.forums_rejoints.get(slug)
                if role_local in ("admin","modo"):
                    act = input("Bannir ou débannir ? (b/d) : ").strip().lower()
                    if act == "b":
                        ok, msg = forum.bannir(cible)
                    elif act == "d":
                        ok, msg = forum.debannir(cible)
                        # if ok:
                        #     other = storage.utilisateurs.get(cible)
                        #     if other:
                        #         other.forums_rejoints.pop(slug, None)
                    couleur.print_jaune(msg)
                    storage.sauvegarder()
                else:
                    couleur.print_rouge("Pas de droits sur ce forum.")
        elif choix == "s":
            slug = input("Forum slug : ").strip()
            fil_id = input("Fil ID : ").strip()
            msg_id = input("Message ID : ").strip()
            role_local = user.forums_rejoints.get(slug)
            if role_local in ("admin","modo"):
                ok, msg = message_service.mod_supprimer_message(user.pseudo, slug, fil_id, msg_id)
                couleur.print_jaune(msg)
            else:
                couleur.print_rouge("Pas de droits pour supprimer.")
        elif choix == "v":
            slug = input("Forum slug : ").strip()
            forum = storage.forums.get(slug)
            role_local = user.forums_rejoints.get(slug)
            if not forum:
                couleur.print_jaune("Forum introuvable.")
            elif role_local == "admin":
                act = input("Verrouiller ou déverrouiller ? (v/d) : ").strip().lower()
                if act == "v":
                    ok, msg = forum.verrouiller()
                else:
                    ok, msg = forum.deverrouiller()
                couleur.print_jaune(msg)
                if ok:
                    storage.sauvegarder()
            else:
                couleur.print_rouge("Seul l'admin peut verrouiller.")
        elif choix == "m":
            slug = input("Forum slug : ").strip()
            target = input("Pseudo à nommer modo : ").strip()
            role_local = user.forums_rejoints.get(slug)
            forum = storage.forums.get(slug)
            if forum and role_local == "admin":
                ok, msg = forum.nommer_moderateur(target)
                couleur.print_jaune(msg)
                if ok:
                    u = storage.utilisateurs.get(target)
                    if u:
                        u.forums_rejoints[slug] = "modo"
                    storage.sauvegarder()
            else:
                couleur.print_rouge("Seul l'admin peut nommer un modo.")
        elif choix == "d":
            slug = input("Forum slug : ").strip()
            forum = storage.forums.get(slug)
            role_local = user.forums_rejoints.get(slug)
            if forum and role_local == "admin":
                storage.forums_supprimes[slug] = forum.en_dict()
                del storage.forums[slug]
                for u in storage.utilisateurs.values():
                    u.forums_rejoints.pop(slug, None)
                storage.sauvegarder()
                couleur.print_jaune("Forum supprimé (backup).")
            else:
                couleur.print_rouge("Seul l'admin peut supprimer le forum.")
        elif choix == "r":
            slug = input("Forum slug : ").strip()
            backup = storage.forums_supprimes.get(slug)
            if not backup:
                couleur.print_jaune("Aucun backup trouvé.")
            else:
                forum = Forum.depuis_dict(backup)
                storage.forums[slug] = forum
                del storage.forums_supprimes[slug]
                storage.sauvegarder()
                couleur.print_jaune("Forum restauré.")
        else:
            couleur.print_rouge("[ERREUR] Option invalide.")
        input("\nAppuyez sur Entrée pour continuer...")

def cli():
    storage.charger()
    user = None
    couleur.print_cyan("\nBienvenue sur la CLI Forum !")
    while True:
        if not user:
            print(dedent("""\
                1. Inscription
                2. Connexion
                0. Quitter
            """))
            choix = input("Choix : ").strip()
            if choix == "1":
                user = page_inscription()
            elif choix == "2":
                user = page_connexion()
            elif choix == "0":
                couleur.print_jaune("Au revoir.")
                break
            else:
                couleur.print_rouge("Option invalide.\n")
        else:
            user = menu_utilisateur(user)

if __name__ == "__main__":
    cli()