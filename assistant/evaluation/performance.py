import time
import json
import psutil
from datetime import datetime
from assistant.config import LOGS_DIR


class PerformanceMonitor:

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.start_ram = None

        self.log_folder = LOGS_DIR
        self.log_folder.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_folder / "performance.jsonl"

    def start_tracking(self):
        self.start_time = time.perf_counter()
        self.start_ram = self.process.memory_info().rss / (1024 * 1024)

    def stop_tracking(self):
        if self.start_time is None:
            raise RuntimeError("Start tracking before stopping.")

        end_time = time.perf_counter()
        end_ram = self.process.memory_info().rss / (1024 * 1024)

        response_time = end_time - self.start_time
        ram_change = end_ram - self.start_ram

        result = {
            "timestamp": datetime.now().isoformat(),
            "response_time": round(response_time, 3),
            "ram_before_mb": round(self.start_ram, 2),
            "ram_after_mb": round(end_ram, 2),
            "ram_change_mb": round(ram_change, 2),
        }

        self.start_time = None
        self.start_ram = None
        return result

    def save_record(self, record):
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(json.dumps(record) + "\n")

    def get_all_records(self):
        if not self.log_file.exists():
            return []

        records = []
        with open(self.log_file, "r", encoding="utf-8") as file:
            for line in file:
                line_str = line.strip()
                if line_str:
                    try:
                        records.append(json.loads(line_str))
                    except json.JSONDecodeError:
                        continue
        return records
