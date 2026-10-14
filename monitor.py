"""System monitoring helpers backed by psutil.

This module contains no Streamlit code so the monitoring logic can be tested
and explained independently from the dashboard.
"""

from __future__ import annotations

import platform
import socket
import time
from datetime import datetime
from typing import Any

import psutil


def _safe_call(function: Any, default: Any = None) -> Any:
    """Return a metric or a clear unavailable value when access is denied."""
    try:
        return function()
    except (OSError, PermissionError, psutil.Error):
        return default


def _bytes_to_gb(value: int | float | None) -> float | None:
    return round(value / (1024**3), 2) if value is not None else None


def _get_processor_name() -> str:
    """Return Windows' friendly CPU model name, with portable fallbacks."""
    if platform.system() == "Windows":
        try:
            import winreg

            key_path = r"HARDWARE\DESCRIPTION\System\CentralProcessor\0"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                if isinstance(name, str) and name.strip():
                    return " ".join(name.split())
        except (OSError, ImportError):
            pass
    return platform.processor() or platform.uname().processor or "Unavailable"


def _get_network_sample() -> tuple[dict[str, Any] | None, str | None, bool]:
    """Read traffic from active physical adapters instead of all system adapters."""
    all_stats = _safe_call(psutil.net_if_stats, {})
    all_counters = _safe_call(lambda: psutil.net_io_counters(pernic=True), {})
    if not all_stats or not all_counters:
        return None, None, False

    eligible = [
        name
        for name, stats in all_stats.items()
        if stats.isup and stats.speed > 0 and name in all_counters and "loopback" not in name.lower()
    ]
    if not eligible:
        eligible = [
            name
            for name, stats in all_stats.items()
            if stats.isup and "loopback" not in name.lower() and name in all_counters
        ]
    if not eligible:
        return None, None, False

    return (
        {
            "bytes_recv": sum(all_counters[name].bytes_recv for name in eligible),
            "bytes_sent": sum(all_counters[name].bytes_sent for name in eligible),
        },
        ", ".join(eligible),
        True,
    )


def get_cpu_metrics() -> dict[str, Any]:
    """Collect current CPU usage, frequency, and core information."""
    frequency = _safe_call(psutil.cpu_freq)
    return {
        "usage": round(psutil.cpu_percent(interval=0.15), 1),
        "per_core_usage": [round(value, 1) for value in psutil.cpu_percent(interval=None, percpu=True)],
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "frequency_mhz": round(frequency.current, 1) if frequency else None,
        "temperature_c": _get_cpu_temperature(),
    }


def _get_cpu_temperature() -> float | None:
    """Read a supported temperature sensor when the operating system exposes one."""
    sensor_reader = getattr(psutil, "sensors_temperatures", None)
    if sensor_reader is None:
        return None
    sensors = _safe_call(sensor_reader, {})
    if not sensors:
        return None
    for readings in sensors.values():
        for reading in readings:
            if reading.current is not None:
                return round(float(reading.current), 1)
    return None


def get_memory_metrics() -> dict[str, Any]:
    """Collect RAM totals and current utilization."""
    memory = psutil.virtual_memory()
    return {
        "usage": round(memory.percent, 1),
        "total_gb": _bytes_to_gb(memory.total),
        "used_gb": _bytes_to_gb(memory.used),
        "available_gb": _bytes_to_gb(memory.available),
    }


def get_disk_metrics() -> dict[str, Any]:
    """Collect disk usage and aggregate disk I/O counters when available."""
    partitions: list[dict[str, Any]] = []
    for partition in psutil.disk_partitions(all=False):
        usage = _safe_call(lambda: psutil.disk_usage(partition.mountpoint))
        if usage is None:
            continue
        partitions.append(
            {
                "device": partition.device or partition.mountpoint,
                "mountpoint": partition.mountpoint,
                "usage": round(usage.percent, 1),
                "total_gb": _bytes_to_gb(usage.total),
                "used_gb": _bytes_to_gb(usage.used),
                "free_gb": _bytes_to_gb(usage.free),
            }
        )

    io_counters = _safe_call(psutil.disk_io_counters)
    return {
        "partitions": partitions,
        "read_bytes": io_counters.read_bytes if io_counters else None,
        "write_bytes": io_counters.write_bytes if io_counters else None,
        "usage": round(max(item["usage"] for item in partitions), 1) if partitions else None,
        "total_gb": round(sum(item["total_gb"] or 0 for item in partitions), 2),
        "used_gb": round(sum(item["used_gb"] or 0 for item in partitions), 2),
        "free_gb": round(sum(item["free_gb"] or 0 for item in partitions), 2),
    }


def get_network_metrics(previous: dict[str, Any] | None = None) -> dict[str, Any]:
    """Collect network totals and calculate speeds from a previous sample."""
    counters, active_interface, connected = _get_network_sample()
    timestamp = time.monotonic()
    if counters is None:
        return {
            "download_mbps": None,
            "upload_mbps": None,
            "received_gb": None,
            "sent_gb": None,
            "interface": None,
            "connected": False,
            "timestamp": timestamp,
        }

    elapsed = max(timestamp - (previous or {}).get("timestamp", timestamp), 0.001)
    received_rate = None
    sent_rate = None
    if previous and counters["bytes_recv"] >= previous.get("bytes_recv", 0):
        received_rate = (counters["bytes_recv"] - previous["bytes_recv"]) / elapsed / (1024**2)
        sent_rate = (counters["bytes_sent"] - previous["bytes_sent"]) / elapsed / (1024**2)

    return {
        "download_mbps": round(received_rate, 2) if received_rate is not None else None,
        "upload_mbps": round(sent_rate, 2) if sent_rate is not None else None,
        "received_gb": round(counters["bytes_recv"] / (1024**3), 3),
        "sent_gb": round(counters["bytes_sent"] / (1024**3), 3),
        "interface": active_interface,
        "connected": connected,
        "timestamp": timestamp,
        "bytes_recv": counters["bytes_recv"],
        "bytes_sent": counters["bytes_sent"],
    }


def get_system_info() -> dict[str, Any]:
    """Collect static operating-system and hardware information."""
    boot_time = _safe_call(psutil.boot_time)
    computer_name = socket.gethostname()
    return {
        "processor": _get_processor_name(),
        "cpu_name": _get_processor_name(),
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "total_ram_gb": _bytes_to_gb(psutil.virtual_memory().total),
        "operating_system": f"{platform.system()} {platform.release()}",
        "computer_name": computer_name,
        "monitoring_host": computer_name,
        "monitoring_scope": "This machine (the host running Streamlit)",
        "python_version": platform.python_version(),
        "boot_time": datetime.fromtimestamp(boot_time) if boot_time else None,
        "architecture": platform.architecture()[0],
    }


def get_processes() -> list[dict[str, Any]]:
    """Return readable process data without attempting to control processes."""
    processes: list[dict[str, Any]] = []
    for process in psutil.process_iter(["name", "cpu_percent", "memory_info", "status"]):
        try:
            info = process.info
            memory = info.get("memory_info")
            processes.append(
                {
                    "name": info.get("name") or "Unavailable",
                    "cpu_percent": round(float(info.get("cpu_percent") or 0), 1),
                    "memory_mb": round(memory.rss / (1024**2), 1) if memory else None,
                    "status": info.get("status") or "Unavailable",
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes


def collect_snapshot(previous_network: dict[str, Any] | None = None) -> dict[str, Any]:
    """Collect one dashboard-ready snapshot using real system metrics."""
    cpu = get_cpu_metrics()
    memory = get_memory_metrics()
    disk = get_disk_metrics()
    network = get_network_metrics(previous_network)
    return {
        "timestamp": datetime.now(),
        "cpu": cpu,
        "ram": memory,
        "disk": disk,
        "network": network,
    }
