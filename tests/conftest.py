import pytest
import json
from pathlib import Path
from storage import stockage


@pytest.fixture(autouse=True)
def isoler_fichier_json(tmp_path, monkeypatch):
    """
    Isole totalement le fichier JSON utilisé par le stockage pour les tests,
    sans modifier storage/stockage.py.

    On redirige simplement :
    - stockage.DATA_FILE
    - stockage.BACKUP_FILE
    vers un dossier temporaire.
    """
    fake_data = tmp_path / "test_data.json"
    fake_backup = tmp_path / "test_data.json.bak"

    # Patch des variables globales du module stockage
    monkeypatch.setattr(stockage, "DATA_FILE", str(fake_data))
    monkeypatch.setattr(stockage, "BACKUP_FILE", str(fake_backup))

    # Initialisation d'un fichier JSON vide pour éviter une erreur de chargement
    fake_data.write_text(json.dumps({
        "utilisateurs": [],
        "forums": [],
        "forums_supprimes": {}
    }), encoding="utf-8")

    # Le stockage doit recharger à partir du fichier temporaire
    stockage.storage.charger()

    yield

    # Nettoyage explicite après les tests
    if fake_data.exists():
        fake_data.unlink()
    if fake_backup.exists():
        fake_backup.unlink()