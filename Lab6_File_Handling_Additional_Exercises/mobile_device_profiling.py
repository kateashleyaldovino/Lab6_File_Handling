
# EXERCISE 2: MOBILE DEVICE USAGE PROFILING

import csv
import json
import shutil
from pathlib import Path

# STUDENT INFORMATION
LAST_NAME = "Aldovino"
STUDENT_ID = "TUMP-26-4168"
SEED_DIGIT = 8
ID_SUM = 27
NAME_LENGTH = 8

# STUDENT-SPECIFIC RULES
TARGET_OS = "Android" if SEED_DIGIT % 2 == 0 else "iOS"
TARGET_BEHAVIOR_CLASS = (SEED_DIGIT % 5) + 1

# PATHS
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
BACKUP_DIR = BASE_DIR / "backup"

OUTPUT_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

INPUT_FILE = DATA_DIR / "user_behavior_dataset.csv"
EXPORTED_FILE = OUTPUT_DIR / "Aldovino_mobile_profile.csv"
JSON_FILE = OUTPUT_DIR / "Aldovino_mobile_summary.json"
BACKUP_FILE = BACKUP_DIR / "Aldovino_mobile_profile_backup.csv"

def find_column(headers, possible_names):
    normalized = {
        str(header).strip().lower().replace(" ", "").replace("_", "")
        .replace("-", "").replace("(", "").replace(")", "")
        .replace("/", "")
        for header in headers
    }

    original = {
        str(header).strip().lower().replace(" ", "").replace("_", "")
        .replace("-", "").replace("(", "").replace(")", "")
        .replace("/", ""): header
        for header in headers
    }

    for name in possible_names:
        key = (
            name.lower().replace(" ", "").replace("_", "")
            .replace("-", "").replace("(", "").replace(")", "")
            .replace("/", "")
        )

        if key in original:
            return original[key]

    raise ValueError(f"Required column not found. Available: {headers}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

selected_records = []
total_records = 0
matching_os_records = 0

battery_values = []
data_usage_values = []

# READ CSV LINE BY LINE
with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)

    if not reader.fieldnames:
        raise ValueError("The CSV file has no header.")

    headers = reader.fieldnames

    user_col = find_column(headers, ["User ID"])
    device_col = find_column(headers, ["Device Model"])
    os_col = find_column(headers, ["Operating System"])
    battery_col = find_column(
        headers, ["Battery Drain (mAh/day)", "Battery Drain"]
    )
    usage_col = find_column(
        headers, ["Data Usage (MB/day)", "Data Usage"]
    )
    behavior_col = find_column(
        headers, ["User Behavior Class", "Behavior Class"]
    )

    for row in reader:
        total_records += 1

        operating_system = str(row.get(os_col, "")).strip()

        if operating_system.lower() == TARGET_OS.lower():
            matching_os_records += 1

            try:
                behavior_class = int(row[behavior_col])

                if behavior_class == TARGET_BEHAVIOR_CLASS:
                    battery = float(row[battery_col])
                    usage = float(row[usage_col])

                    selected_records.append({
                        "User ID": row[user_col],
                        "Device Model": row[device_col],
                        "Operating System": row[os_col],
                        "Battery Drain (mAh/day)": battery,
                        "Data Usage (MB/day)": usage
                    })

                    battery_values.append(battery)
                    data_usage_values.append(usage)

            except (ValueError, TypeError, KeyError):
                # Skip records with missing or invalid target values
                continue

# COMPUTE AVERAGES
selected_count = len(selected_records)

average_battery = (
    sum(battery_values) / len(battery_values)
    if battery_values else 0
)

average_data_usage = (
    sum(data_usage_values) / len(data_usage_values)
    if data_usage_values else 0
)

# EXPORT REQUIRED FIELDS TO CSV
export_fields = [
    "User ID",
    "Device Model",
    "Operating System",
    "Battery Drain (mAh/day)",
    "Data Usage (MB/day)"
]

with open(EXPORTED_FILE, "w", encoding="utf-8", newline="") as output:
    writer = csv.DictWriter(output, fieldnames=export_fields)
    writer.writeheader()
    writer.writerows(selected_records)

# CREATE JSON SUMMARY
summary = {
    "student": LAST_NAME,
    "student_id": STUDENT_ID,
    "target_operating_system": TARGET_OS,
    "target_behavior_class": TARGET_BEHAVIOR_CLASS,
    "total_records_in_dataset": total_records,
    "records_matching_operating_system": matching_os_records,
    "records_in_target_behavior_class": selected_count,
    "average_battery_drain_mAh_per_day": round(average_battery, 2),
    "average_data_usage_MB_per_day": round(average_data_usage, 2),
    "exported_record_count": selected_count,
    "count_verified": selected_count == len(selected_records),
    "exported_csv_file": EXPORTED_FILE.name
}

with open(JSON_FILE, "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=4)

# VERIFY JSON COUNT
with open(JSON_FILE, "r", encoding="utf-8") as file:
    saved_summary = json.load(file)

count_verified = (
    saved_summary["exported_record_count"] == len(selected_records)
)

# BACKUP EXPORTED CSV
shutil.copy2(EXPORTED_FILE, BACKUP_FILE)

backup_verified = BACKUP_FILE.exists()
backup_size = BACKUP_FILE.stat().st_size if backup_verified else 0

# DISPLAY RESULTS
print("=== MOBILE DEVICE USAGE PROFILING ===")
print("Student:", LAST_NAME)
print("Student ID:", STUDENT_ID)
print("Operating System:", TARGET_OS)
print("Target Behavior Class:", TARGET_BEHAVIOR_CLASS)
print("Total records in dataset:", total_records)
print("Records matching operating system:", matching_os_records)
print("Records in target behavior class:", selected_count)
print("Average battery drain (mAh/day):", round(average_battery, 2))
print("Average data usage (MB/day):", round(average_data_usage, 2))
print("Count verification:", count_verified)
print("Exported CSV:", EXPORTED_FILE)
print("JSON summary:", JSON_FILE)
print("Backup file:", BACKUP_FILE)
print("Backup size:", backup_size, "bytes")
print("Backup verification:", backup_verified)
print("\nFINAL OUTPUT: Mobile usage profiling completed.")
