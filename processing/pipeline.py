import pandas as pd


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all data-cleaning steps (pure pandas, no Streamlit):
      - Create binary `has_cabin` flag before dropping Cabin
      - Fill missing Age with the median
      - Fill missing Embarked with the mode
      - Drop the Cabin column
    Returns a cleaned copy.
    """
    df = df.copy()

    # Binary flag: 1 if the passenger had a recorded cabin, else 0
    df["has_cabin"] = df["Cabin"].notna().astype(int)

    # Age: fill NaNs with the median (robust to outliers from high-fare 1st-class passengers)
    df["Age"] = df["Age"].fillna(df["Age"].median())

    # Embarked: fill the 2 NaNs with the mode (Southampton — most common port)
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Drop Cabin — 77% missing makes reliable imputation impossible
    df = df.drop(columns=["Cabin"])

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived feature columns:
      - AgeGroup: Child (<13) | Teen (13-19) | Adult (20-59) | Senior (60+)
      - Title: extracted from Name using str methods; rare titles → 'Rare'
    Returns an enriched copy.
    """
    df = df.copy()

    # ── AgeGroup ──────────────────────────────────────────────────────────────
    bins   = [0, 12, 19, 59, 120]
    labels = ["Child", "Teen", "Adult", "Senior"]
    df["AgeGroup"] = pd.cut(df["Age"], bins=bins, labels=labels).astype(str)

    # ── Title ─────────────────────────────────────────────────────────────────
    # Name format: "Last, Title. First Middle (optional)"
    df["Title"] = (
        df["Name"]
        .str.split(",").str[1]   # everything after the comma
        .str.split(".").str[0]   # everything before the first dot
        .str.strip()             # remove surrounding whitespace
    )
    _common = {"Mr", "Miss", "Mrs", "Master", "Dr", "Rev"}
    df["Title"] = df["Title"].apply(lambda t: t if t in _common else "Rare")

    return df


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Apply sidebar filter selections to the enriched DataFrame.
    `filters` must be: {"pclass": [int, ...], "sex": [str, ...]}
    Returns a filtered copy.
    """
    mask = (
        df["Pclass"].isin(filters["pclass"]) &
        df["Sex"].isin(filters["sex"])
    )
    return df[mask].copy()
