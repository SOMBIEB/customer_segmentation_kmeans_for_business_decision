# src/data/process_features.py

# =========================
# Data Process (Feature Processing)
# =========================
# Objectif :
# - Lire le fichier nettoyé issu du Data Cleaning : data/interim/cleaned_data.csv
# - Créer une variable "data_keep" (liste de features à garder) directement dans le code
# - Créer les features métier nécessaires (Age, total_spending, since_customer, total_children, AcceptedAny)
# - Garder uniquement les colonnes de data_keep
# - Encoder les catégorielles (si besoin) + Scaler les numériques
# - Sauvegarder le résultat dans data/processed/features_scaled.csv + preprocessor.joblib
# =========================

from pathlib import Path
import pandas as pd

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from joblib import dump

from scipy.sparse import spmatrix, issparse


def X_to_dataframe(X, feature_names):
    """
    Convertit X (numpy array ou sparse matrix) en DataFrame pandas.
    Utile car OneHotEncoder peut produire une matrice sparse.
    """
    if issparse(X):
        X = X.toarray()  # sparse -> dense (OK sur ton dataset)
    return pd.DataFrame(X, columns=feature_names)


def add_business_features(df: pd.DataFrame, config: dict, data_keep: list[str]) -> pd.DataFrame:
    """
    Crée des features métier uniquement si elles sont demandées dans data_keep.
    """
    out = df.copy()

    # --- Age ---
    # Age = année actuelle - Year_Birth
    if "Age" in data_keep:
        if "Year_Birth" in out.columns:
            current_year = pd.Timestamp("today").year
            out["Age"] = current_year - pd.to_numeric(out["Year_Birth"], errors="coerce")
        else:
            # Si Year_Birth absent, on crée Age à 0 pour ne pas planter
            out["Age"] = 0

    # --- total_children ---
    # total_children = Kidhome + Teenhome
    if "total_children" in data_keep:
        out["total_children"] = out.get("Kidhome", 0) + out.get("Teenhome", 0)

    # --- total_spending ---
    # total_spending = somme des montants Mnt*
    if "total_spending" in data_keep:
        spend_cols = [
            "MntWines", "MntFruits", "MntMeatProducts",
            "MntFishProducts", "MntSweetProducts", "MntGoldProds"
        ]
        spend_cols = [c for c in spend_cols if c in out.columns]
        if spend_cols:
            out["total_spending"] = out[spend_cols].sum(axis=1)
        else:
            out["total_spending"] = 0

    # --- since_customer ---
    # since_customer = nombre de jours depuis Dt_Customer
    if "since_customer" in data_keep:
        date_col = config["dataset"].get("date_col", "Dt_Customer")
        if date_col in out.columns:
            dates = pd.to_datetime(out[date_col], dayfirst=True, errors="coerce")
            out["since_customer"] = (pd.Timestamp("today") - dates).dt.days
        else:
            out["since_customer"] = 0

    # --- AcceptedAny ---
    # AcceptedAny = a accepté au moins une campagne (cmp1..cmp5 + Response)
    if "AcceptedAny" in data_keep:
        campaign_cols = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5", "Response"]
        campaign_cols = [c for c in campaign_cols if c in out.columns]
        if campaign_cols:
            out["AcceptedAny"] = (out[campaign_cols].sum(axis=1) > 0).astype(int)
        else:
            out["AcceptedAny"] = 0

    return out


def run_feature_processing(config: dict):
    """
    Pipeline complet Data Process :
    - utilise cleaned_data.csv (sortie Data Cleaning)
    - crée data_keep (hardcodé)
    - crée les features métier demandées
    - filtre selon data_keep
    - encode + scale
    - sauvegarde data/processed/features_scaled.csv + preprocessor.joblib
    """

    # =========================
    # 0) ✅ DATA KEEP (ta liste)
    # =========================
    # Tu m'as donné cet exemple, donc on le prend tel quel :
    data_keep = [
        "Income",
        "total_spending",
        "since_customer",
        "Age",
        "total_children",
        "Recency",
        "NumStorePurchases",
        "NumWebPurchases",
        "AcceptedAny",
    ]

    # =========================
    # 1) Chemins
    # =========================
    interim_dir = Path(config["paths"]["interim"])        # ex: data/interim
    processed_dir = Path(config["paths"]["processed"])    # ex: data/processed
    processed_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = interim_dir / "cleaned_data.csv"
    if not cleaned_path.exists():
        raise FileNotFoundError(
            f"{cleaned_path} introuvable.\n"
            "➡️ Lance d'abord le Data Cleaning pour générer cleaned_data.csv."
        )

    # =========================
    # 2) Lire le dataset CLEAN (pas le raw)
    # =========================
    df_clean = pd.read_csv(cleaned_path)

    # =========================
    # 3) Créer les features métier demandées
    # =========================
    df_feat = add_business_features(df_clean, config, data_keep)

    # =========================
    # 4) Garder uniquement data_keep (si les colonnes existent)
    # =========================
    existing = [c for c in data_keep if c in df_feat.columns]
    missing = [c for c in data_keep if c not in df_feat.columns]

    if len(existing) == 0:
        raise ValueError(
            "Aucune feature de data_keep n'existe dans le dataframe.\n"
            f"data_keep: {data_keep}\n"
            f"Colonnes dispo: {list(df_feat.columns)}"
        )

    # On informe juste (sans bloquer) si certaines features sont absentes
    if missing:
        print("⚠️ Features de data_keep absentes (ignorées) :", missing)

    df_selected = df_feat[existing].copy()

    # =========================
    # 5) Séparer numériques vs catégorielles
    # =========================
    cat_cols = df_selected.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    num_cols = [c for c in df_selected.columns if c not in cat_cols]

    # =========================
    # 6) Imputation simple (évite NaN)
    # =========================
    # Numériques -> médiane
    for c in num_cols:
        df_selected[c] = pd.to_numeric(df_selected[c], errors="coerce")
        df_selected[c] = df_selected[c].fillna(df_selected[c].median())

    # Catégorielles -> "Unknown"
    for c in cat_cols:
        df_selected[c] = df_selected[c].fillna("Unknown").astype(str)

    # =========================
    # 7) Encoder + Scaler
    # =========================
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=True), cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False
    )

    X = preprocessor.fit_transform(df_selected)

    # =========================
    # 8) Récupérer les noms de features après transformation
    # =========================
    try:
        feature_names = preprocessor.get_feature_names_out().tolist()
    except Exception:
        feature_names = [f"f_{i}" for i in range(X.shape[1])]

    # =========================
    # 9) Sauvegarde (CSV final + pipeline)
    # =========================
    df_X = X_to_dataframe(X, feature_names)

    out_csv = processed_dir / "features_scaled.csv"
    out_pipe = processed_dir / "preprocessor.joblib"

    df_X.to_csv(out_csv, index=False)
    dump(preprocessor, out_pipe)

    print("✅ Data Process terminé")
    print("➡️ Fichier final :", out_csv.resolve())
    print("➡️ Pipeline sauvegardé :", out_pipe.resolve())
    print("➡️ data_keep utilisé :", data_keep)

    # On retourne aussi data_keep pour que tu le voies dans le notebook
    return df_selected, X, feature_names, data_keep
