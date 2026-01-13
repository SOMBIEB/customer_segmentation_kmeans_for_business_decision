# src/data/clean_data.py

# =========================
# Nettoyage des données (Data Cleaning)
# =========================
# Objectif :
# - Lire les données brutes (data/raw)
# - Nettoyer ce qui est "qualité de données" (doublons, types, dates, NA)
# - Sauvegarder un fichier propre dans data/interim/cleaned_data.csv
#
# IMPORTANT :
# - Ici on ne fait PAS de scaling, PAS d'encodage.
# - On prépare juste une base propre et cohérente.
# =========================

from pathlib import Path
import pandas as pd


def clean_raw_data(config: dict) -> pd.DataFrame:
    """
    Nettoie le dataset brut puis sauvegarde le résultat dans data/interim/cleaned_data.csv

    Parameters
    ----------
    config : dict
        Configuration chargée depuis config.yaml

    Returns
    -------
    pd.DataFrame
        Dataframe nettoyé
    """

    # ---------- 1) Charger les données brutes ----------
    # Import local (évite des soucis de dépendances circulaires)
    from src.data.load_data import load_raw_data

    df = load_raw_data(config)   # lit data/raw/ + filename
    df = df.copy()               # sécurité : on évite de modifier l'original

    # ---------- 2) Colonnes clés depuis config ----------
    id_col = config["dataset"].get("id_col", None)        # ex: ID
    date_col = config["dataset"].get("date_col", None)    # ex: Dt_Customer

    # ---------- 3) Supprimer les doublons ----------
    # Doublons exacts sur toutes les colonnes
    df = df.drop_duplicates()

    # Doublons sur la colonne ID (si elle existe)
    if id_col and id_col in df.columns:
        df = df.drop_duplicates(subset=[id_col], keep="first")

    # ---------- 4) Conversion date ----------
    # On veut que Dt_Customer soit un vrai datetime
    if date_col and date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors="coerce")
        # errors="coerce" => si une date est invalide -> NaT au lieu de crash

    # ---------- 5) Income : conversion + imputation ----------
    # Dans ce dataset, Income a souvent des NA.
    if "Income" in df.columns:
        # Convertir en numérique (au cas où ça arrive en texte)
        df["Income"] = pd.to_numeric(df["Income"], errors="coerce")

        # Imputation médiane : robuste aux outliers
        median_income = df["Income"].median()
        df["Income"] = df["Income"].fillna(median_income)

    # ---------- 6) Colonnes numériques : coercion "safe" ----------
    numeric_cols = [
        "Year_Birth", "Recency",
        "Kidhome", "Teenhome",
        "MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds",
        "NumDealsPurchases", "NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases", "NumWebVisitsMonth",
        "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5", "Response",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ---------- 7) Remplir les NA des compteurs/montants par 0 ----------
    # Logique métier : si un compteur est manquant, on suppose 0.
    fill_zero_cols = [
        "Kidhome", "Teenhome",
        "MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds",
        "NumDealsPurchases", "NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases", "NumWebVisitsMonth",
        "AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5", "Response",
        "Recency",
    ]
    for col in fill_zero_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    # ---------- 8) Sauvegarde dans data/interim ----------
    interim_dir = Path(config["paths"]["interim"])  # ex: data/interim
    interim_dir.mkdir(parents=True, exist_ok=True)

    out_path = interim_dir / "cleaned_data.csv"
    df.to_csv(out_path, index=False)

    return df
    print(f"✅ Données nettoyées sauvegardées dans : {out_path}")
   