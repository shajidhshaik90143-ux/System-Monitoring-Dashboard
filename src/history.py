from collections import deque
from datetime import datetime
import pandas as pd

class HistoryStore:
    def __init__(self, max_points=240):
        self.max_points = max_points
        self.rows = deque(maxlen=max_points)

    def add(self, cpu, memory, disk, download, upload):
        self.rows.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "cpu": round(cpu, 2),
            "memory": round(memory, 2),
            "disk": round(disk, 2),
            "download_mbps": round(download, 3),
            "upload_mbps": round(upload, 3),
        })

    def dataframe(self):
        return pd.DataFrame(list(self.rows))
