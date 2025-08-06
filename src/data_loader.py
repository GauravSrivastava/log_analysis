import os
import re
from datetime import datetime

def load_logs(log_folder="sample_data/logs"):
    log_entries = []
    log_pattern = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*?method=(?P<method>\w+).*?endpoint=(?P<endpoint>\S+).*?status=(?P<status>\d+)(?:.*?response_time=(?P<response_time>\d+)ms)?'
    )

    for filename in os.listdir(log_folder):
        filepath = os.path.join(log_folder, filename)
        if os.path.isfile(filepath):
            with open(filepath, "r") as file:
                lines = file.readlines()
                for line in lines:
                    match = log_pattern.search(line)
                    if match:
                        entry = match.groupdict()
                        entry["timestamp"] = datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                        entry["status"] = int(entry["status"])
                        entry["response_time"] = int(entry["response_time"]) if entry["response_time"] else None
                        log_entries.append(entry)
    return log_entries
