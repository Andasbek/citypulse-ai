import pandas as pd

from utils.constants import (
    ECOLOGY_AQI_NORMAL,
    ECOLOGY_AQI_WARNING,
    STATUS_NORMAL,
    STATUS_WARNING,
    STATUS_CRITICAL,
)


def get_ecology_kpis(df: pd.DataFrame) -> dict:
    return {
        "avg_aqi": round(df["aqi"].mean(), 1),
        "avg_pm25": round(df["pm25"].mean(), 1),
        "avg_pm10": round(df["pm10"].mean(), 1),
    }


def get_ecology_status(avg_aqi: float) -> str:
    if avg_aqi <= ECOLOGY_AQI_NORMAL:
        return STATUS_NORMAL
    if avg_aqi <= ECOLOGY_AQI_WARNING:
        return STATUS_WARNING
    return STATUS_CRITICAL


def get_aqi_by_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("timestamp")["aqi"].mean().reset_index()


def get_aqi_by_district(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("district")["aqi"]
        .mean()
        .reset_index()
        .sort_values("aqi", ascending=False)
    )


def get_district_stats(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("district")
        .agg(
            avg_aqi=("aqi", "mean"),
            avg_pm25=("pm25", "mean"),
            avg_pm10=("pm10", "mean"),
        )
        .reset_index()
        .sort_values("avg_aqi", ascending=False)
    )
