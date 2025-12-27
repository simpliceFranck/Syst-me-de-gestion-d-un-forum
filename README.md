# GestionForumAvance

Bienvenue dans **GestionForumAvance**, une application de type forum en ligne fonctionnant via une interface en ligne de commande (CLI). Ce projet permet aux utilisateurs de créer, rejoindre et gérer des forums, des fils de discussion et des messages, avec des fonctionnalités avancées de modération et de messagerie privée.

---

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Contributions](#contributions)
- [Licence](#licence)

---

## Fonctionnalités

L'application permet de :

- S'inscrire et se connecter en tant qu'utilisateur.
- Créer, rejoindre et quitter des forums.
- Créer des fils de discussion et publier des messages.
- Liker ou disliker des messages.
- Modifier ses messages.
- Lire ses notifications et sa messagerie privée (MP).
- Rechercher du texte dans les messages.
- Fonctions de modération :
  - Bannir/débannir des membres.
  - Nommer des modérateurs.
  - Verrouiller/déverrouiller des forums.
  - Supprimer et restaurer des forums (avec backup).

---

## Installation

1. **Cloner le dépôt :**

```bash
git clone https://github.com/votre-utilisateur/GestionForumAvance.git
cd GestionForumAvance
Créer un environnement virtuel (optionnel mais recommandé) :

bash
Copier le code
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Installer les dépendances :

Aucune dépendance externe n’est requise pour cette version (tout est en Python standard).

Lancer l'application :

bash
Copier le code
python main.py
Utilisation
L'application fonctionne entièrement via une interface en ligne de commande (CLI).

Menu principal :
1 : Inscription

2 : Connexion

0 : Quitter

Menu utilisateur :
Après connexion, vous aurez accès à toutes les fonctionnalités du forum, telles que :

Lister et rejoindre des forums

Créer des forums et des fils

Publier et gérer des messages

Gestion des notifications et messages privés

Fonctions de modération (si administrateur ou modérateur)

L'interface est interactive et vous guide étape par étape avec des invites claires.

Structure du projet
graphql
Copier le code
GestionForumAvance/
│
├─ main.py                 # Point d'entrée de l'application
├─ utils/
│   └─ couleurs.py         # Gestion des couleurs pour la CLI
├─ storage/
│   └─ stockage.py         # Gestion du stockage et sauvegarde
├─ services/
│   ├─ forum_service.py
│   ├─ fil_service.py
│   ├─ message_service.py
│   ├─ mp_service.py
│   ├─ search_service.py
│   └─ notification_service.py
├─ ui/
│   └─ console_ui.py       # Interface CLI pour afficher les forums, inbox, etc.
└─ models/
    └─ forum.py            # Classe Forum et sérialisation/désérialisation