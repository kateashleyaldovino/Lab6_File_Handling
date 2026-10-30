
# EXERCISE 1: WEB SERVER ACCESS LOG ANALYSIS

import csv
import json
import shutil
from pathlib import Path
from collections import Counter

# STUDENT INFORMATION
LAST_NAME = "Aldovino"
STUDENT_ID = "TUMP-26-4168"
SEED_DIGIT = 8
ID_SUM = 27
NAME_LENGTH = 8

# PATHS
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
BACKUP_DIR = BASE_DIR / "backup"

OUTPUT_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

INPUT_FILE = DATA_DIR / "webog.csv"
FILTERED_FILE = OUTPUT_DIR / "Aldovino_web_filtered.csv"
JSON_FILE = OUTPUT_DIR / "Aldovino_web_summary.json"
BACKUP_FILE = BACKUP_DIR / "Aldovino_web_summary_backup.json"

# STUDENT-SPECIFIC RULES
RECORD_LIMIT = 1000 + ID_SUM
TARGET_STATUS_CLASS = (SEED_DIGIT % 4) + 2

# FIND A COLUMN USING ITS POSSIBLE HEADER NAMES
def find_column(headers, possible_names):
    normalized = {
        str(header).strip().lower().replace(" ", "").replace("_", "")
        .replace("-", ""): header
        for header in headers
    }

    for name in possible_names:
        key = name.lower().replace(" ", "").replace("_", "").replace("-", "")
        if key in normalized:
            return normalized[key]

    raise ValueError(
        f"Required column not found. Available columns: {headers}"
    )

# VALIDATE INPUT FILE
if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

records_processed = 0
selected_records = []
status_counts = Counter()
url_counts = Counter()

with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)

    if not reader.fieldnames:
        raise ValueError("The CSV file has no header.")

    headers = reader.fieldnames

    ip_col = find_column(headers, ["IP", "IP Address", "Client IP"])
    time_col = find_column(headers, ["Time", "Timestamp", "Date"])
    url_col = find_column(headers, ["URL", "Requested URL", "Request"])
    status_col = find_column(headers, ["Status", "Staus", "HTTP Status", "Status Code"])

    with open(FILTERED_FILE, "w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()

        for row in reader:
            if records_processed >= RECORD_LIMIT:
                break

            records_processed += 1

            try:
                status_text = str(row.get(status_col, "")).strip()
                status_code = int(status_text)

                if status_code // 100 == TARGET_STATUS_CLASS:
                    selected_records.append(row)
                    status_counts[status_code] += 1

                    requested_url = str(row.get(url_col, "")).strip()
                    if requested_url:
                        url_counts[requested_url] += 1

                    writer.writerow(row)

            except (ValueError, TypeError):
                # Skip records with invalid or missing status codes
                continue

# FIVE MOST FREQUENT URLS
top_five_urls = url_counts.most_common(5)

# JSON SUMMARY
summary = {
    "student": LAST_NAME,
    "student_id": STUDENT_ID,
    "records_processed": records_processed,
    "target_status_class": f"{TARGET_STATUS_CLASS}xx",
    "records_in_target_class": len(selected_records),
    "count_per_status_code": dict(status_counts),
    "five_most_requested_urls": [
        {"url": url, "requests": count}
        for url, count in top_five_urls
    ],
    "filtered_csv_file": FILTERED_FILE.name
}

with open(JSON_FILE, "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=4)

# BACKUP AND VERIFY
shutil.copy2(JSON_FILE, BACKUP_FILE)
backup_verified = BACKUP_FILE.exists()

# DISPLAY RESULTS
print("=== WEB SERVER ACCESS LOG ANALYSIS ===")
print("Student:", LAST_NAME)
print("Student ID:", STUDENT_ID)
print("Records processed:", records_processed)
print("Target status class:", f"{TARGET_STATUS_CLASS}xx")
print("Records in target class:", len(selected_records))
print("Count per status code:", dict(status_counts))

print("\nFive most requested URLs:")
for url, count in top_five_urls:
    print(url, "=", count)

print("\nFiltered CSV:", FILTERED_FILE)
print("JSON summary:", JSON_FILE)
print("Backup file:", BACKUP_FILE)
print("Backup verification:", backup_verified)
print("\nFINAL OUTPUT: Web log analysis completed.")
