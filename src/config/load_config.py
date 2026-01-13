# =========================
# Configuration Loader
# =========================

import yaml
from pathlib import Path


def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    Charge le fichier de configuration YAML du projet.

    Parameters
    ----------
    config_path : str
        Chemin vers le fichier config.yaml

    Returns
    -------
    dict
        Dictionnaire contenant toute la configuration du projet
    """

    # Conversion du chemin en objet Path (plus robuste que les strings)
    config_path = Path(config_path)

    # Vérification que le fichier existe
    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration introuvable : {config_path}")

    # Ouverture et lecture du fichier YAML
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config
