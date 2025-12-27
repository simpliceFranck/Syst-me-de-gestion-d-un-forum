from datetime import datetime, timezone

def utc_now():
    # Récupère l'heure actuelle en UTC, retire les microsecondes, convertit en ISO,
    # puis remplace "+00:00" par "Z" pour indiquer explicitement l'UTC.
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

"""Exemple de sortie :
makefile
Copier le code
2025-11-29T14:32:08Z
⚡ Remarque
Le Z signifie Zulu time, qui est juste un autre nom pour UTC.
C’est le format ISO le plus court et le plus standard dans les systèmes et APIs."""