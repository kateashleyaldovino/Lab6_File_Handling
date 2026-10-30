
# EXERCISE 3: CYBERSECURITY INCIDENT REPORT

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

# STUDENT-SPECIFIC TARGET YEAR
TARGET_YEAR = 2015 + SEED_DIGIT

# PATHS
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
BACKUP_DIR = BASE_DIR / "backup"

OUTPUT_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

INPUT_FILE = DATA_DIR / "Global_Cybersecurity_Threats_2015-2024.csv"
FILTERED_FILE = OUTPUT_DIR / "Aldovino_cybersecurity_2023.csv"
JSON_FILE = OUTPUT_DIR / "Aldovino_cybersecurity_summary.json"
BACKUP_FILE = BACKUP_DIR / "Aldovino_cybersecurity_summary_backup.json"
REPORT_FILE = OUTPUT_DIR / "Aldovino_cybersecurity_report.txt"

def normalize(value):
    return (
        str(value).strip().lower()
        .replace(" ", "").replace("_", "")
        .replace("-", "").replace("(", "").replace(")", "")
        .replace("$", "").replace("/", "")
    )

def find_column(headers, possible_names):
    normalized_headers = {normalize(h): h for h in headers}

    for name in possible_names:
        key = normalize(name)
        if key in normalized_headers:
            return normalized_headers[key]

    raise ValueError(
        f"Required column not found. Available columns: {headers}"
    )

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"Dataset not found: {INPUT_FILE}")

total_records = 0
target_incidents = []
attack_counts = Counter()
financial_losses = []

# READ CSV LINE BY LINE
with open(INPUT_FILE, "r", encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source)

    if not reader.fieldnames:
        raise ValueError("The CSV file has no header.")

    headers = reader.fieldnames

    year_col = find_column(headers, ["Year"])
    attack_col = find_column(headers, ["Attack Type"])
    loss_col = find_column(
        headers,
        ["Financial Loss (in Million $)", "Financial Loss", "Financial Loss (Million $)"]
    )

    for original_position, row in enumerate(reader):
        total_records += 1

        try:
            year = int(float(str(row.get(year_col, "")).strip()))

            if year != TARGET_YEAR:
                continue

            attack_type = str(row.get(attack_col, "")).strip()
            loss = float(str(row.get(loss_col, "")).replace(",", "").strip())

            if not attack_type or loss < 0:
                continue

            target_incidents.append({
                "original_position": original_position,
                "row": row,
                "attack_type": attack_type,
                "loss": loss
            })

            attack_counts[attack_type] += 1
            financial_losses.append(loss)

        except (ValueError, TypeError):
            # Skip invalid year or financial loss values
            continue

# TOTAL AND AVERAGE FINANCIAL LOSS
incident_count = len(target_incidents)

total_loss = sum(financial_losses)
average_loss = (
    total_loss / len(financial_losses)
    if financial_losses else 0
)

# STABLE DESCENDING SORT:
# Equal losses retain their original dataset order.
costliest = sorted(
    target_incidents,
    key=lambda incident: -incident["loss"]
)[:5]

# EXPORT TARGET-YEAR RECORDS TO CSV
with open(FILTERED_FILE, "w", encoding="utf-8", newline="") as output:
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()

    for incident in target_incidents:
        writer.writerow(incident["row"])

# BUILD JSON SUMMARY
summary = {
    "student": LAST_NAME,
    "student_id": STUDENT_ID,
    "target_year": TARGET_YEAR,
    "total_records_in_dataset": total_records,
    "incidents_in_target_year": incident_count,
    "count_per_attack_type": dict(attack_counts),
    "total_financial_loss_usd_millions": round(total_loss, 2),
    "average_financial_loss_usd_millions": round(average_loss, 2),
    "five_costliest_incidents": [
        {
            "original_dataset_position": item["original_position"],
            "attack_type": item["attack_type"],
            "financial_loss_usd_millions": item["loss"]
        }
        for item in costliest
    ],
    "filtered_csv_file": FILTERED_FILE.name
}

with open(JSON_FILE, "w", encoding="utf-8") as file:
    json.dump(summary, file, indent=4)

# BACKUP JSON AND VERIFY
shutil.copy2(JSON_FILE, BACKUP_FILE)

backup_verified = BACKUP_FILE.exists()

# GENERATE TEXT REPORT
with open(REPORT_FILE, "w", encoding="utf-8") as report:
    report.write("CYBERSECURITY INCIDENT REPORT\n")
    report.write("============================\n")
    report.write(f"Student: {LAST_NAME}\n")
    report.write(f"Student ID: {STUDENT_ID}\n")
    report.write(f"Target Year: {TARGET_YEAR}\n")
    report.write(f"Total Records in Dataset: {total_records}\n")
    report.write(f"Incidents in Target Year: {incident_count}\n\n")

    report.write("COUNT PER ATTACK TYPE\n")
    for attack, count in attack_counts.items():
        report.write(f"{attack}: {count}\n")

    report.write("\nFINANCIAL LOSS\n")
    report.write(f"Total: {total_loss:.2f} USD million\n")
    report.write(f"Average: {average_loss:.2f} USD million\n")

    report.write("\nFIVE COSTLIEST INCIDENTS\n")
    for rank, item in enumerate(costliest, 1):
        report.write(
            f"{rank}. {item['attack_type']} - "
            f"{item['loss']:.2f} USD million "
            f"(original position: {item['original_position']})\n"
        )

    report.write(f"\nFiltered CSV: {FILTERED_FILE.name}\n")
    report.write(f"JSON Summary: {JSON_FILE.name}\n")
    report.write(f"Backup Verified: {backup_verified}\n")

# DISPLAY RESULTS
print("=== CYBERSECURITY INCIDENT REPORT ===")
print("Student:", LAST_NAME)
print("Student ID:", STUDENT_ID)
print("Target year:", TARGET_YEAR)
print("Total records in dataset:", total_records)
print("Incidents in target year:", incident_count)
print("Count per attack type:", dict(attack_counts))
print("Total financial loss (USD millions):", round(total_loss, 2))
print("Average financial loss (USD millions):", round(average_loss, 2))

print("\nFive costliest incidents:")
for rank, item in enumerate(costliest, 1):
    print(
        rank,
        item["attack_type"],
        "-",
        round(item["loss"], 2),
        "USD million"
    )

print("\nFiltered CSV:", FILTERED_FILE)
print("JSON summary:", JSON_FILE)
print("Backup verification:", backup_verified)
print("Report file:", REPORT_FILE)
print("\nFINAL OUTPUT: Cybersecurity incident report completed.")
