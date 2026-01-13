# =========================
# Data Loading
# =========================

from pathlib import Path
import pandas as pd


def load_raw_data(config: dict) -> pd.DataFrame:
    """
    Charge le dataset brut depuis data/raw en se basant sur config/config.yaml.

    Parameters
    ----------
    config : dict
        Configuration du projet (load_config())

    Returns
    -------
    pd.DataFrame
        Données brutes chargées
    """

    raw_dir = Path(config["paths"]["raw"])
    filename = config["dataset"]["filename"]
    file_path = raw_dir / filename

    # Vérification existence fichier
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset introuvable : {file_path}\n"
            f"➡️ Vérifie que le fichier est bien dans {raw_dir}"
        )

    # Lecture CSV
    df = pd.read_csv(file_path)

    # Vérification colonnes minimales (basé sur ton dataset)
    id_col = config["dataset"]["id_col"]
    date_col = config["dataset"]["date_col"]

    missing_cols = [c for c in [id_col, date_col] if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Colonnes attendues manquantes : {missing_cols}\n"
            f"Colonnes disponibles : {list(df.columns)}"
        )

    return df


def load_processed_data(config: dict, filename: str) -> pd.DataFrame:
    """
    Charge un fichier depuis data/processed/ (utile après preprocessing).

    Parameters
    ----------
    config : dict
        Configuration du projet
    filename : str
        Nom du fichier à charger (ex: features_scaled.csv)

    Returns
    -------
    pd.DataFrame
    """

    processed_dir = Path(config["paths"]["processed"])
    file_path = processed_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(f"Fichier processed introuvable : {file_path}")

    return pd.read_csv(file_path)
