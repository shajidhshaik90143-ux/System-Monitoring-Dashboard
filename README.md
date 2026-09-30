# System Monitoring Dashboard

A strong real-time desktop/server monitoring dashboard built with **Python + Streamlit + psutil**.

## Features

- Real-time CPU monitoring
- CPU frequency and core information
- RAM and swap monitoring
- Disk usage and mounted partition monitoring
- Network download/upload rate
- Network interface status and addresses
- Top running processes
- CPU/memory/disk threshold alerts
- Performance history charts
- Machine and OS information
- Boot-time information
- Temperature sensors when supported by the operating system
- Auto-refresh mode
- Configurable alert thresholds
- Responsive Streamlit UI

## Project Structure

```text
System Monitoring Dashboard/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── monitor.py
│   └── history.py
├── data/
└── logs/
```

## Windows Setup

```powershell
cd "System Monitoring Dashboard"
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Troubleshooting

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

If `streamlit` is not recognized:

```powershell
python -m streamlit run app.py
```

If a package is missing:

```powershell
python -m pip install -r requirements.txt
```

## Notes

- Some process details require administrator privileges.
- Temperature sensors are OS/hardware dependent.
- Disk partition visibility depends on permissions.
- Network speed is measured during a short sampling window.
