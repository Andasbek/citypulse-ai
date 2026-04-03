import pandas as pd

from utils.constants import (
    TRANSPORT_CONGESTION_NORMAL,
    TRANSPORT_CONGESTION_WARNING,
    TRANSPORT_SPEED_CRITICAL,
    TRANSPORT_INCIDENTS_HIGH,
    ECOLOGY_AQI_NORMAL,
    ECOLOGY_AQI_WARNING,
    STATUS_NORMAL,
    STATUS_WARNING,
    STATUS_CRITICAL,
)


def _transport_severity(row: pd.Series) -> str:
    if row["congestion_level"] >= TRANSPORT_CONGESTION_WARNING:
        severity = STATUS_CRITICAL
    elif row["congestion_level"] >= TRANSPORT_CONGESTION_NORMAL:
        severity = STATUS_WARNING
    else:
        return STATUS_NORMAL

    if row["avg_speed"] < TRANSPORT_SPEED_CRITICAL:
        severity = STATUS_CRITICAL
    if row["incidents_count"] >= TRANSPORT_INCIDENTS_HIGH:
        severity = STATUS_CRITICAL
    return severity


def _ecology_severity(row: pd.Series) -> str:
    if row["aqi"] > ECOLOGY_AQI_WARNING:
        return STATUS_CRITICAL
    if row["aqi"] > ECOLOGY_AQI_NORMAL:
        return STATUS_WARNING
    return STATUS_NORMAL


def detect_transport_issues(df: pd.DataFrame) -> list[dict]:
    issues = []
    for _, row in df.iterrows():
        severity = _transport_severity(row)
        if severity == STATUS_NORMAL:
            continue
        desc_parts = []
        if row["congestion_level"] >= TRANSPORT_CONGESTION_NORMAL:
            desc_parts.append(f"загруженность {row['congestion_level']}%")
        if row["avg_speed"] < TRANSPORT_SPEED_CRITICAL:
            desc_parts.append(f"скорость {row['avg_speed']} км/ч")
        if row["incidents_count"] >= TRANSPORT_INCIDENTS_HIGH:
            desc_parts.append(f"инцидентов: {row['incidents_count']}")
        issues.append(
            {
                "type": "Транспорт",
                "district": row["district"],
                "timestamp": row["timestamp"],
                "severity": severity,
                "description": ", ".join(desc_parts),
            }
        )
    return issues


def detect_ecology_issues(df: pd.DataFrame) -> list[dict]:
    issues = []
    for _, row in df.iterrows():
        severity = _ecology_severity(row)
        if severity == STATUS_NORMAL:
            continue
        desc_parts = [f"AQI {row['aqi']}"]
        if row["pm25"] > 35:
            desc_parts.append(f"PM2.5: {row['pm25']}")
        if row["pm10"] > 50:
            desc_parts.append(f"PM10: {row['pm10']}")
        issues.append(
            {
                "type": "Экология",
                "district": row["district"],
                "timestamp": row["timestamp"],
                "severity": severity,
                "description": ", ".join(desc_parts),
            }
        )
    return issues
