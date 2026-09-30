import streamlit as st
import pandas as pd
import psutil
import platform
import socket
import time
from datetime import datetime
from pathlib import Path

from src.monitor import (
    get_system_info, get_cpu_metrics, get_memory_metrics,
    get_disk_metrics, get_network_metrics, get_processes,
    get_temperatures, get_boot_time, get_alerts
)
from src.history import HistoryStore

st.set_page_config(
    page_title="System Monitoring Dashboard",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.metric-card {
    padding: 16px 18px; border-radius: 14px; border: 1px solid rgba(128,128,128,.22);
    background: rgba(128,128,128,.06); margin-bottom: 8px;
}
.small {font-size: .82rem; opacity: .72;}
.status-ok {font-weight: 700;}
.alert-box {
    border-left: 5px solid #ff4b4b; padding: 12px 16px; border-radius: 8px;
    background: rgba(255,75,75,.08); margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = HistoryStore()
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

history = st.session_state.history

st.sidebar.title("🖥️ System Monitor")
st.sidebar.caption("Real-time workstation monitoring")

auto = st.sidebar.toggle("Auto refresh", value=True)
interval = st.sidebar.slider("Refresh interval (seconds)", 2, 30, 5)
cpu_limit = st.sidebar.slider("CPU alert threshold (%)", 50, 100, 85)
memory_limit = st.sidebar.slider("Memory alert threshold (%)", 50, 100, 85)
disk_limit = st.sidebar.slider("Disk alert threshold (%)", 50, 100, 90)
process_count = st.sidebar.slider("Processes to display", 5, 50, 15)

if st.sidebar.button("🔄 Refresh now", use_container_width=True):
    st.rerun()

info = get_system_info()
cpu = get_cpu_metrics()
memory = get_memory_metrics()
disk = get_disk_metrics()
network = get_network_metrics()
temps = get_temperatures()
processes = get_processes(process_count)
boot = get_boot_time()

history.add(cpu["percent"], memory["percent"], disk["percent"], network["download_mbps"], network["upload_mbps"])

alerts = get_alerts(cpu["percent"], memory["percent"], disk["percent"], cpu_limit, memory_limit, disk_limit)

st.title("System Monitoring Dashboard")
st.caption(f"Live monitoring • Last updated {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")

# Overview
st.subheader("📊 System Overview")
c1, c2, c3, c4 = st.columns(4)
c1.metric("CPU Usage", f"{cpu['percent']:.1f}%", f"{cpu['frequency']:.0f} MHz")
c2.metric("Memory Usage", f"{memory['percent']:.1f}%", f"{memory['used_gb']:.1f}/{memory['total_gb']:.1f} GB")
c3.metric("Disk Usage", f"{disk['percent']:.1f}%", f"{disk['used_gb']:.1f}/{disk['total_gb']:.1f} GB")
c4.metric("Network", f"↓ {network['download_mbps']:.2f} MB/s", f"↑ {network['upload_mbps']:.2f} MB/s")

if alerts:
    st.subheader("🚨 Active Alerts")
    for alert in alerts:
        st.markdown(f'<div class="alert-box">⚠️ {alert}</div>', unsafe_allow_html=True)
else:
    st.success("✅ All configured resource thresholds are currently normal.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Performance", "💾 Storage", "🌐 Network", "⚙️ Processes", "🖥️ System Info"
])

with tab1:
    st.subheader("Performance History")
    hist = history.dataframe()
    if not hist.empty:
        st.line_chart(hist.set_index("time")[["cpu", "memory", "disk"]], height=360)
    else:
        st.info("Collecting performance history...")

    a, b = st.columns(2)
    with a:
        st.markdown("### CPU")
        st.progress(min(cpu["percent"] / 100, 1.0))
        st.write(f"**{cpu['percent']:.1f}%** utilization")
        st.write(f"Logical CPUs: **{cpu['logical']}**")
        st.write(f"Physical CPUs: **{cpu['physical']}**")
    with b:
        st.markdown("### Memory")
        st.progress(min(memory["percent"] / 100, 1.0))
        st.write(f"**{memory['percent']:.1f}%** utilization")
        st.write(f"Available: **{memory['available_gb']:.1f} GB**")
        st.write(f"Swap: **{memory['swap_percent']:.1f}%**")

with tab2:
    st.subheader("Disk & Storage")
    st.metric("Primary Disk", f"{disk['percent']:.1f}% used")
    st.progress(min(disk["percent"] / 100, 1.0))
    st.write(f"Used: **{disk['used_gb']:.2f} GB**")
    st.write(f"Free: **{disk['free_gb']:.2f} GB**")
    st.write(f"Total: **{disk['total_gb']:.2f} GB**")

    st.markdown("### Mounted Partitions")
    parts = disk["partitions"]
    if parts:
        st.dataframe(pd.DataFrame(parts), use_container_width=True, hide_index=True)
    else:
        st.info("No readable partitions found.")

with tab3:
    st.subheader("Network Monitoring")
    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Download", f"{network['download_mbps']:.2f} MB/s")
    n2.metric("Upload", f"{network['upload_mbps']:.2f} MB/s")
    n3.metric("Packets In", f"{network['packets_recv']:,}")
    n4.metric("Packets Out", f"{network['packets_sent']:,}")

    net_hist = history.dataframe()
    if not net_hist.empty:
        st.line_chart(net_hist.set_index("time")[["download_mbps", "upload_mbps"]], height=320)

    st.markdown("### Network Interfaces")
    st.dataframe(pd.DataFrame(network["interfaces"]), use_container_width=True, hide_index=True)

with tab4:
    st.subheader("Top Running Processes")
    if processes:
        pdf = pd.DataFrame(processes)
        st.dataframe(
            pdf.style.format({"cpu": "{:.1f}", "memory": "{:.1f}"}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Process data unavailable.")

with tab5:
    st.subheader("Machine Information")
    left, right = st.columns(2)
    with left:
        st.write("**Hostname:**", info["hostname"])
        st.write("**Operating System:**", info["os"])
        st.write("**OS Version:**", info["version"])
        st.write("**Architecture:**", info["architecture"])
        st.write("**Processor:**", info["processor"] or "Unknown")
    with right:
        st.write("**Boot Time:**", boot)
        st.write("**Python:**", platform.python_version())
        st.write("**CPU Cores:**", cpu["physical"], "physical /", cpu["logical"], "logical")
        if temps:
            st.write("**Temperatures:**")
            for t in temps:
                st.write(f"- {t['label']}: {t['current']:.1f} °C")

st.divider()
st.caption("System Monitoring Dashboard • Built with Python, Streamlit and psutil")

if auto:
    time.sleep(interval)
    st.rerun()
