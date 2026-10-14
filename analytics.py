"""History, analytics, health scoring, and alert rules for the analyzer."""

from __future__ import annotations

from collections import deque
from typing import Any, Iterable

import pandas as pd


class MetricsHistory:
    """Bounded metric history that ignores duplicate timestamps."""

    def __init__(self, max_points: int = 600) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=max_points)
        self._last_timestamp: Any = None

    def add(self, snapshot: dict[str, Any]) -> bool:
        timestamp = snapshot.get("timestamp")
        if timestamp == self._last_timestamp:
            return False
        self._items.append(snapshot)
        self._last_timestamp = timestamp
        return True

    def items(self) -> list[dict[str, Any]]:
        return list(self._items)

    def dataframe(self) -> pd.DataFrame:
        rows = []
        for item in self._items:
            rows.append(
                {
                    "Timestamp": item["timestamp"],
                    "CPU": item["cpu"].get("usage"),
                    "RAM": item["ram"].get("usage"),
                    "Disk": item["disk"].get("usage"),
                    "Download": item["network"].get("download_mbps"),
                    "Upload": item["network"].get("upload_mbps"),
                }
            )
        return pd.DataFrame(rows, columns=["Timestamp", "CPU", "RAM", "Disk", "Download", "Upload"])


def _values(history: Iterable[dict[str, Any]], section: str, key: str) -> list[float]:
    values = []
    for snapshot in history:
        value = snapshot.get(section, {}).get(key)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return values


def summarize_history(history: Iterable[dict[str, Any]]) -> dict[str, float | None]:
    """Calculate transparent average, minimum, and peak values."""
    cpu = _values(history, "cpu", "usage")
    ram = _values(history, "ram", "usage")
    download = _values(history, "network", "download_mbps")
    upload = _values(history, "network", "upload_mbps")
    network = download + upload

    def average(values: list[float]) -> float | None:
        return round(sum(values) / len(values), 1) if values else None

    def peak(values: list[float]) -> float | None:
        return round(max(values), 1) if values else None

    return {
        "average_cpu": average(cpu),
        "minimum_cpu": round(min(cpu), 1) if cpu else None,
        "maximum_cpu": peak(cpu),
        "average_ram": average(ram),
        "minimum_ram": round(min(ram), 1) if ram else None,
        "maximum_ram": peak(ram),
        "average_network": average(network),
        "peak_network": peak(network),
    }


def health_score(snapshot: dict[str, Any]) -> tuple[int, dict[str, str]]:
    """Return a 0-100 score using understandable utilization penalties."""
    cpu = snapshot.get("cpu", {}).get("usage")
    ram = snapshot.get("ram", {}).get("usage")
    disk = snapshot.get("disk", {}).get("usage")
    checks: dict[str, str] = {}
    score = 100

    for label, value, warning, critical in (
        ("CPU", cpu, 70, 85),
        ("RAM", ram, 70, 85),
        ("Disk", disk, 70, 90),
    ):
        if not isinstance(value, (int, float)):
            checks[label] = "Unavailable"
            continue
        if value >= critical:
            score -= 30
            checks[label] = "Critical"
        elif value >= warning:
            score -= 15
            checks[label] = "High"
        else:
            checks[label] = "Normal"

    network = snapshot.get("network", {})
    checks["Network"] = "Connected" if network.get("connected") else "Unavailable"
    return max(0, score), checks


def alerts(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    """Return threshold alerts for the current snapshot."""
    results = []
    rules = (
        ("CPU", snapshot.get("cpu", {}).get("usage"), 85, "%"),
        ("RAM", snapshot.get("ram", {}).get("usage"), 85, "%"),
        ("Disk", snapshot.get("disk", {}).get("usage"), 90, "%"),
    )
    for label, value, threshold, unit in rules:
        if isinstance(value, (int, float)) and value > threshold:
            results.append(
                {
                    "title": f"High {label} usage",
                    "message": f"{label} usage is {value:.1f}{unit}, above the configured {threshold}{unit} threshold.",
                }
            )
    return results


def insights(snapshot: dict[str, Any], process_rows: list[dict[str, Any]] | None = None) -> list[str]:
    """Generate short observations from current metrics."""
    messages = []
    for label, value in (
        ("CPU", snapshot.get("cpu", {}).get("usage")),
        ("RAM", snapshot.get("ram", {}).get("usage")),
        ("Disk", snapshot.get("disk", {}).get("usage")),
    ):
        if not isinstance(value, (int, float)):
            messages.append(f"{label} usage is currently unavailable.")
        elif value >= 85:
            messages.append(f"{label} usage is high.")
        elif value >= 70:
            messages.append(f"{label} usage is moderately high.")
        else:
            messages.append(f"{label} usage is currently normal.")
    if process_rows:
        top_process = max(process_rows, key=lambda row: row.get("memory_mb") or 0)
        messages.append(f"{top_process['name']} is currently the highest RAM-consuming process.")
    return messages
