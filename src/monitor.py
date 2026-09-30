import os
import platform
import socket
from datetime import datetime
import psutil

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
    }

def get_cpu_metrics():
    freq = psutil.cpu_freq()
    return {
        "percent": psutil.cpu_percent(interval=0.4),
        "frequency": freq.current if freq else 0,
        "logical": psutil.cpu_count(logical=True) or 0,
        "physical": psutil.cpu_count(logical=False) or 0,
    }

def get_memory_metrics():
    m = psutil.virtual_memory()
    s = psutil.swap_memory()
    gb = 1024 ** 3
    return {
        "percent": m.percent,
        "used_gb": m.used / gb,
        "total_gb": m.total / gb,
        "available_gb": m.available / gb,
        "swap_percent": s.percent,
    }

def get_disk_metrics():
    root = os.path.abspath(os.sep)
    try:
        d = psutil.disk_usage(root)
    except Exception:
        d = psutil.disk_usage(".")
    gb = 1024 ** 3
    partitions = []
    for p in psutil.disk_partitions(all=False):
        try:
            u = psutil.disk_usage(p.mountpoint)
            partitions.append({
                "device": p.device,
                "mountpoint": p.mountpoint,
                "filesystem": p.fstype,
                "total_gb": round(u.total / gb, 2),
                "used_gb": round(u.used / gb, 2),
                "free_gb": round(u.free / gb, 2),
                "usage_%": round(u.percent, 1),
            })
        except (PermissionError, OSError):
            pass
    return {
        "percent": d.percent,
        "used_gb": d.used / gb,
        "total_gb": d.total / gb,
        "free_gb": d.free / gb,
        "partitions": partitions,
    }

def get_network_metrics():
    counters = psutil.net_io_counters()
    interfaces = []
    pernic = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    for name, stats in pernic.items():
        interfaces.append({
            "interface": name,
            "status": "Up" if stats.isup else "Down",
            "speed_mbps": stats.speed,
            "addresses": ", ".join(a.address for a in addrs.get(name, [])),
        })

    # A short measurement window gives an actual transfer rate.
    before = counters
    import time
    time.sleep(0.25)
    after = psutil.net_io_counters()
    download = max(0, after.bytes_recv - before.bytes_recv) / 0.25 / (1024 ** 2)
    upload = max(0, after.bytes_sent - before.bytes_sent) / 0.25 / (1024 ** 2)

    return {
        "download_mbps": download,
        "upload_mbps": upload,
        "packets_recv": after.packets_recv,
        "packets_sent": after.packets_sent,
        "interfaces": interfaces,
    }

def get_processes(limit=15):
    rows = []
    for p in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent", "status"]):
        try:
            x = p.info
            rows.append({
                "pid": x["pid"],
                "name": x["name"] or "Unknown",
                "user": x["username"] or "System",
                "cpu": x["cpu_percent"] or 0.0,
                "memory": x["memory_percent"] or 0.0,
                "status": x["status"],
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    rows.sort(key=lambda x: (x["cpu"], x["memory"]), reverse=True)
    return rows[:limit]

def get_temperatures():
    result = []
    try:
        data = psutil.sensors_temperatures()
        for group, entries in data.items():
            for e in entries:
                result.append({"label": e.label or group, "current": e.current})
    except (AttributeError, NotImplementedError):
        pass
    return result

def get_boot_time():
    return datetime.fromtimestamp(psutil.boot_time()).strftime("%d %b %Y, %I:%M:%S %p")

def get_alerts(cpu, memory, disk, cpu_limit, memory_limit, disk_limit):
    alerts = []
    if cpu >= cpu_limit:
        alerts.append(f"CPU usage is {cpu:.1f}% (threshold {cpu_limit}%).")
    if memory >= memory_limit:
        alerts.append(f"Memory usage is {memory:.1f}% (threshold {memory_limit}%).")
    if disk >= disk_limit:
        alerts.append(f"Disk usage is {disk:.1f}% (threshold {disk_limit}%).")
    return alerts
