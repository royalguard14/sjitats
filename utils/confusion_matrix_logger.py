import csv
import os
from datetime import datetime

CSV_FILE = "logs/confusion_matrix.csv"

def log_result(predicted, actual):
    os.makedirs("logs", exist_ok=True)

    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "predicted", "actual"])

        writer.writerow([
            datetime.now().isoformat(),
            predicted,
            actual
        ])
