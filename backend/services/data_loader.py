import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_transport() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "transport.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def load_ecology() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "ecology.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
