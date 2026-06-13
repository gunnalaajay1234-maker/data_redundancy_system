from colorama import Fore, Style, init
from tabulate import tabulate
from database import init_db
from validator import validate_record
from cloud_storage import store_record, fetch_all_records, fetch_rejected
from duplicate_checker import log_rejection, log_audit

init(autoreset=True)

# ─── Sample incoming data (includes duplicates + invalid entries) ───────────
incoming_data = [
    {"name": "Ajay Kumar",     "email": "ajay@zaltix.com",    "category": "technology", "value": 4500.00},
    {"name": "Priya Sharma",   "email": "priya@example.com",  "category": "finance",    "value": 1200.50},
    {"name": "Ravi Reddy",     "email": "ravi@cloud.io",      "category": "healthcare", "value": 890.00},
    {"name": "Ajay Kumar",     "email": "ajay@zaltix.com",    "category": "technology", "value": 4500.00},  # DUPLICATE
    {"name": "   ",            "email": "invalid-email",      "category": "retail",     "value": 100},       # INVALID
    {"name": "Sneha Patel",    "email": "sneha@edu.in",       "category": "education",  "value": 300.75},
    {"name": "Ravi Reddy",     "email": "ravi@cloud.io",      "category": "healthcare", "value": 890.00},   # DUPLICATE
    {"name": "Admin123",       "email": "admin@test.com",     "category": "unknown",    "value": 0},         # INVALID category
    {"name": "Meena Joshi",    "email": "meena@retail.com",   "category": "retail",     "value": -50},       # INVALID negative
    {"name": "Kiran Babu",     "email": "kiran@finance.net",  "category": "finance",    "value": 9999.99},
]

def process_all(data):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"  DATA REDUNDANCY REMOVAL SYSTEM — PROCESSING {len(data)} RECORDS")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    results = {"stored": 0, "duplicate": 0, "invalid": 0}

    for i, record in enumerate(data, 1):
        print(f"{Fore.YELLOW}[{i:02d}] Processing: {record}{Style.RESET_ALL}")

        # Step A: Validate
        is_valid, reason = validate_record(record)
        if not is_valid:
            print(f"  {Fore.RED}✗ INVALID — {reason}{Style.RESET_ALL}")
            log_rejection(record, f"INVALID: {reason}")
            log_audit("REJECTED_INVALID", "N/A", reason)
            results["invalid"] += 1
            continue

        # Step B: Check duplicate + store
        result = store_record(record)

        if result["status"] == "success":
            print(f"  {Fore.GREEN}✔ STORED  — {result['message']}{Style.RESET_ALL}")
            results["stored"] += 1
        elif result["status"] == "duplicate":
            print(f"  {Fore.MAGENTA}⚠ DUPLICATE — {result['message']}{Style.RESET_ALL}")
            results["duplicate"] += 1
        else:
            print(f"  {Fore.RED}✗ ERROR — {result['message']}{Style.RESET_ALL}")

    return results

def show_summary(results):
    print(f"\n{Fore.CYAN}{'='*60}")
    print("  PROCESSING SUMMARY")
    print(f"{'='*60}{Style.RESET_ALL}")
    summary = [
        ["✔ Successfully Stored",  results["stored"]],
        ["⚠ Duplicates Rejected",  results["duplicate"]],
        ["✗ Invalid Records",       results["invalid"]],
        ["TOTAL Processed",         sum(results.values())],
    ]
    print(tabulate(summary, headers=["Status", "Count"], tablefmt="fancy_grid"))

def show_cloud_records():
    rows = fetch_all_records()
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  CLOUD DATABASE — UNIQUE VERIFIED RECORDS ({len(rows)} total)")
    print(f"{'='*60}{Style.RESET_ALL}")
    headers = ["ID", "Name", "Email", "Category", "Value (₹)", "Stored At"]
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

def show_rejected():
    rows = fetch_rejected()
    print(f"\n{Fore.RED}{'='*60}")
    print(f"  REJECTED RECORDS LOG ({len(rows)} total)")
    print(f"{'='*60}{Style.RESET_ALL}")
    headers = ["ID", "Raw Data", "Reason", "Rejected At"]
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid", maxcolwidths=40))

if __name__ == "__main__":
    init_db()                        # Step 1: Initialize DB
    results = process_all(incoming_data)  # Step 2: Process all records
    show_summary(results)            # Step 3: Print summary
    show_cloud_records()             # Step 4: Show clean cloud data
    show_rejected()                  # Step 5: Show rejected log