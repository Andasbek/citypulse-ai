import pandas as pd

from utils.constants import (
    TRANSPORT_CONGESTION_NORMAL,
    TRANSPORT_CONGESTION_WARNING,
    STATUS_NORMAL,
    STATUS_WARNING,
    STATUS_CRITICAL,
)


def get_transport_kpis(df: pd.DataFrame) -> dict:
    return {
        "avg_speed": round(df["avg_speed"].mean(), 1),
        "avg_congestion": round(df["congestion_level"].mean(), 1),
        "total_incidents": int(df["incidents_count"].sum()),
    }


def get_transport_status(avg_congestion: float) -> str:
    if avg_congestion < TRANSPORT_CONGESTION_NORMAL:
        return STATUS_NORMAL
    if avg_congestion < TRANSPORT_CONGESTION_WARNING:
        return STATUS_WARNING
    return STATUS_CRITICAL


def get_congestion_by_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("timestamp")["congestion_level"].mean().reset_index()


def get_congestion_by_district(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("district")["congestion_level"]
        .mean()
        .reset_index()
        .sort_values("congestion_level", ascending=False)
    )


def get_district_stats(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("district")
        .agg(
            avg_speed=("avg_speed", "mean"),
            avg_congestion=("congestion_level", "mean"),
            total_incidents=("incidents_count", "sum"),
        )
        .reset_index()
        .sort_values("avg_congestion", ascending=False)
    )
