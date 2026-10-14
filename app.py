"""Streamlit entry point for the PC Performance Analyzer."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from analytics import MetricsHistory, alerts, health_score, insights, summarize_history
from monitor import collect_snapshot, get_processes, get_system_info


st.set_page_config(
    page_title="PC Performance Analyzer",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = {
    "background": "#0B0F14",
    "sidebar": "#10151C",
    "card": "#151B23",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
    "accent": "#38BDF8",
    "success": "#4ADE80",
    "warning": "#FBBF24",
    "critical": "#F87171",
}


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{ background: {COLORS["background"]}; color: {COLORS["text"]}; }}
        [data-testid="stSidebar"] {{ background: {COLORS["sidebar"]}; }}
        [data-testid="stMetric"] {{
            background: {COLORS["card"]}; border: 1px solid #24303D;
            border-radius: 12px; padding: 16px;
        }}
        [data-testid="stMetricLabel"] {{ color: {COLORS["muted"]}; }}
        .status {{ color: {COLORS["success"]}; font-weight: 600; }}
        .subtle {{ color: {COLORS["muted"]}; font-size: 0.9rem; }}
        .card {{
            background: {COLORS["card"]}; border: 1px solid #24303D;
            border-radius: 12px; padding: 18px; height: 100%;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_value(value: Any, suffix: str = "") -> str:
    return f"{value:.1f}{suffix}" if isinstance(value, (int, float)) else "Unavailable"


def format_gb(value: Any) -> str:
    return f"{value:.2f} GB" if isinstance(value, (int, float)) else "Unavailable"


def get_time_greeting(hour: int | None = None) -> str:
    """Return a greeting based on the local time of day."""
    current_hour = datetime.now().hour if hour is None else hour
    if 4 <= current_hour < 12:
        return "Good Morning"
    if 12 <= current_hour < 17:
        return "Good Afternoon"
    if 17 <= current_hour < 22:
        return "Good Evening"
    return "Good Night"


def make_line_chart(data: pd.DataFrame, columns: list[str], title: str, y_title: str) -> go.Figure:
    figure = go.Figure()
    for column in columns:
        if column in data and data[column].notna().any():
            figure.add_trace(
                go.Scatter(
                    x=data["Timestamp"],
                    y=data[column],
                    mode="lines",
                    name=column,
                    line={"width": 2},
                )
            )
    figure.update_layout(
        title=title,
        yaxis_title=y_title,
        yaxis={"range": [0, 100] if y_title == "Usage (%)" else None},
        height=300,
        margin={"l": 10, "r": 10, "t": 45, "b": 10},
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        font={"color": COLORS["text"]},
        legend={"orientation": "h", "y": 1.12},
        hovermode="x unified",
    )
    return figure


def metric_card(label: str, value: str, detail: str) -> None:
    st.markdown(
        f'<div class="card"><div class="subtle">{label}</div>'
        f'<h2 style="margin: 8px 0 4px;">{value}</h2>'
        f'<div class="subtle">{detail}</div></div>',
        unsafe_allow_html=True,
    )


def initialize_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = MetricsHistory(max_points=600)
    if "previous_network" not in st.session_state:
        st.session_state.previous_network = None
    if "last_snapshot" not in st.session_state:
        st.session_state.last_snapshot = None
    if "thresholds" not in st.session_state:
        st.session_state.thresholds = {"cpu": 85, "ram": 85, "disk": 90}


def read_snapshot() -> dict[str, Any]:
    snapshot = collect_snapshot(st.session_state.previous_network)
    st.session_state.previous_network = snapshot["network"]
    st.session_state.history.add(snapshot)
    st.session_state.last_snapshot = snapshot
    return snapshot


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("## ◉ PC Performance Analyzer")
        st.caption("Windows system monitoring dashboard")
        page = st.radio(
            "Navigation",
            ["Dashboard", "Analytics", "Processes", "System Information"],
            format_func=lambda value: {
                "Dashboard": "📊 Overview",
                "Analytics": "📈 Analytics",
                "Processes": "⚙ Processes",
                "System Information": "💻 System",
            }[value],
        )
        st.divider()
        st.markdown("### Alert thresholds")
        st.session_state.thresholds["cpu"] = st.slider("CPU alert (%)", 50, 100, 85)
        st.session_state.thresholds["ram"] = st.slider("RAM alert (%)", 50, 100, 85)
        st.session_state.thresholds["disk"] = st.slider("Disk alert (%)", 50, 100, 90)
        st.divider()
        st.caption("Metrics refresh automatically every 2 seconds.")
    return page


def threshold_alerts(snapshot: dict[str, Any]) -> list[dict[str, str]]:
    configured = st.session_state.thresholds
    values = (
        ("CPU", snapshot["cpu"].get("usage"), configured["cpu"]),
        ("RAM", snapshot["ram"].get("usage"), configured["ram"]),
        ("Disk", snapshot["disk"].get("usage"), configured["disk"]),
    )
    return [
        {
            "title": f"High {label} usage",
            "message": f"{label} is {value:.1f}%, above your configured {limit}% threshold.",
        }
        for label, value, limit in values
        if isinstance(value, (int, float)) and value > limit
    ]


def render_header(snapshot: dict[str, Any]) -> None:
    left, right = st.columns([4, 1])
    with left:
        system_info = get_system_info()
        st.title(f"{get_time_greeting()} {system_info['computer_name']}")
        st.write("Performance of the machine running this Streamlit app.")
    with right:
        st.markdown('<p class="status">● Monitoring live</p>', unsafe_allow_html=True)
        st.caption(snapshot["timestamp"].strftime("%H:%M:%S"))
    st.info(
        f"Monitoring host: **{system_info['monitoring_host']}** · "
        "These are metrics from the computer where Streamlit is running."
    )


def render_dashboard(snapshot: dict[str, Any]) -> None:
    render_header(snapshot)
    cpu, ram, disk, network = snapshot["cpu"], snapshot["ram"], snapshot["disk"], snapshot["network"]
    metric_columns = st.columns(4)
    with metric_columns[0]:
        metric_card("CPU", format_value(cpu.get("usage"), "%"), f"{cpu.get('logical_cores') or 'Unavailable'} logical cores")
    with metric_columns[1]:
        metric_card("RAM", format_value(ram.get("usage"), "%"), f"{format_gb(ram.get('used_gb'))} / {format_gb(ram.get('total_gb'))}")
    with metric_columns[2]:
        metric_card("DISK", format_value(disk.get("usage"), "%"), f"{format_gb(disk.get('free_gb'))} free")
    with metric_columns[3]:
        metric_card("DOWNLOAD", format_value(network.get("download_mbps"), " MB/s"), network.get("interface") or "No active interface")

    st.write("")
    chart_columns = st.columns([2, 1])
    history_df = st.session_state.history.dataframe()
    with chart_columns[0]:
        if history_df.empty:
            st.info("Collecting history...")
        else:
            st.plotly_chart(make_line_chart(history_df, ["CPU", "RAM"], "CPU and RAM performance", "Usage (%)"), use_container_width=True)
    with chart_columns[1]:
        score, checks = health_score(snapshot)
        st.markdown("### System health")
        st.metric("Health score", f"{score}/100")
        for label, state in checks.items():
            icon = "✓" if state in {"Normal", "Connected"} else "⚠"
            st.write(f"{icon} {label}: {state}")

    st.markdown("### Network activity")
    network_columns = st.columns(3)
    network_columns[0].metric("Download", format_value(network.get("download_mbps"), " MB/s"))
    network_columns[1].metric("Upload", format_value(network.get("upload_mbps"), " MB/s"))
    network_columns[2].metric("Total received", format_gb(network.get("received_gb")))
    if not history_df.empty:
        st.plotly_chart(make_line_chart(history_df, ["Download", "Upload"], "Network activity", "Speed (MB/s)"), use_container_width=True)

    current_alerts = threshold_alerts(snapshot)
    if current_alerts:
        st.markdown("### Alerts")
        for item in current_alerts:
            st.warning(f"**{item['title']}** — {item['message']}")


def render_analytics() -> None:
    st.title("Performance Analytics")
    history_df = st.session_state.history.dataframe()
    if history_df.empty:
        st.info("Collecting readings. Analytics will appear after the first sample.")
        return
    window = st.selectbox("Time window", ["Last 1 minute", "Last 5 minutes", "Last 10 minutes"], index=1)
    minutes = int(window.split()[1])
    cutoff = pd.Timestamp.now() - pd.Timedelta(minutes=minutes)
    filtered = history_df[history_df["Timestamp"] >= cutoff]
    summary = summarize_history(st.session_state.history.items())
    metric_columns = st.columns(4)
    metric_columns[0].metric("Average CPU", format_value(summary["average_cpu"], "%"))
    metric_columns[1].metric("Peak CPU", format_value(summary["maximum_cpu"], "%"))
    metric_columns[2].metric("Average RAM", format_value(summary["average_ram"], "%"))
    metric_columns[3].metric("Peak network", format_value(summary["peak_network"], " MB/s"))
    st.plotly_chart(make_line_chart(filtered, ["CPU"], "CPU usage", "Usage (%)"), use_container_width=True)
    st.plotly_chart(make_line_chart(filtered, ["RAM"], "RAM usage", "Usage (%)"), use_container_width=True)
    st.plotly_chart(make_line_chart(filtered, ["Download", "Upload"], "Network activity", "Speed (MB/s)"), use_container_width=True)
    st.markdown("### Insights")
    for message in insights(st.session_state.last_snapshot or {}, get_processes()[:100]):
        st.write(f"• {message}")
    st.download_button(
        "Generate CSV report",
        data=history_df.to_csv(index=False).encode("utf-8"),
        file_name=f"performance-report-{datetime.now():%Y%m%d-%H%M%S}.csv",
        mime="text/csv",
        use_container_width=False,
    )


def render_processes() -> None:
    st.title("Running Processes")
    process_rows = get_processes()
    if not process_rows:
        st.warning("Process information is unavailable.")
        return
    process_df = pd.DataFrame(process_rows)
    search = st.text_input("Search process", placeholder="Type a process name...")
    sort_by = st.selectbox("Sort by", ["CPU usage", "RAM usage", "Name"])
    if search:
        process_df = process_df[process_df["name"].str.contains(search, case=False, na=False)]
    sort_column = {"CPU usage": "cpu_percent", "RAM usage": "memory_mb", "Name": "name"}[sort_by]
    process_df = process_df.sort_values(sort_column, ascending=sort_by == "Name").head(100)
    process_df = process_df.rename(
        columns={"name": "Process", "cpu_percent": "CPU (%)", "memory_mb": "RAM (MB)", "status": "Status"}
    )
    st.dataframe(process_df, hide_index=True, use_container_width=True)
    st.caption(f"Showing {len(process_df)} of {len(process_rows)} accessible processes. No process controls are provided.")


def render_system_info() -> None:
    st.title("System Information")
    info = get_system_info()
    fields = [
        ("Processor", info["processor"]),
        ("CPU cores", f"{info['physical_cores'] or 'Unavailable'} physical / {info['logical_cores'] or 'Unavailable'} logical"),
        ("Memory", format_gb(info["total_ram_gb"])),
        ("Operating system", info["operating_system"]),
        ("Computer name", info["computer_name"]),
        ("Monitoring host", info["monitoring_scope"]),
        ("Architecture", info["architecture"]),
        ("Python", info["python_version"]),
        ("Boot time", info["boot_time"].strftime("%Y-%m-%d %H:%M") if info["boot_time"] else "Unavailable"),
    ]
    columns = st.columns(2)
    for index, (label, value) in enumerate(fields):
        with columns[index % 2]:
            st.markdown(f'<div class="card"><div class="subtle">{label}</div><h4>{value}</h4></div>', unsafe_allow_html=True)
            st.write("")


def main() -> None:
    initialize_state()
    inject_styles()
    page = render_sidebar()

    @st.fragment(run_every="2s")
    def live_page() -> None:
        snapshot = read_snapshot()
        if page == "Dashboard":
            render_dashboard(snapshot)
        elif page == "Analytics":
            render_analytics()
        elif page == "Processes":
            render_processes()
        else:
            render_system_info()

    live_page()


if __name__ == "__main__":
    main()
