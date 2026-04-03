import pandas as pd

from utils.constants import (
    TRANSPORT_CONGESTION_WARNING,
    ECOLOGY_AQI_WARNING,
    STATUS_CRITICAL,
)


def get_combined_data(transport_df: pd.DataFrame, ecology_df: pd.DataFrame) -> pd.DataFrame:
    t_agg = (
        transport_df.groupby("district")
        .agg(avg_congestion=("congestion_level", "mean"), avg_speed=("avg_speed", "mean"))
        .reset_index()
    )
    e_agg = (
        ecology_df.groupby("district")
        .agg(avg_aqi=("aqi", "mean"), avg_pm25=("pm25", "mean"))
        .reset_index()
    )
    merged = t_agg.merge(e_agg, on="district")
    merged["risk_score"] = (
        merged["avg_congestion"] * 0.4 + merged["avg_aqi"] * 0.6
    ).round(1)
    return merged.sort_values("risk_score", ascending=False)


def detect_combined_issues(transport_df: pd.DataFrame, ecology_df: pd.DataFrame) -> list[dict]:
    merged = transport_df.merge(
        ecology_df, on=["district", "timestamp"], suffixes=("_t", "_e")
    )
    issues = []
    for _, row in merged.iterrows():
        if (
            row["congestion_level"] >= TRANSPORT_CONGESTION_WARNING
            and row["aqi"] > ECOLOGY_AQI_WARNING
        ):
            issues.append(
                {
                    "type": "Комбинированная",
                    "district": row["district"],
                    "timestamp": row["timestamp"],
                    "severity": STATUS_CRITICAL,
                    "description": (
                        f"Загруженность {row['congestion_level']}%, "
                        f"AQI {row['aqi']}, скорость {row['avg_speed']} км/ч"
                    ),
                }
            )
    return issues
