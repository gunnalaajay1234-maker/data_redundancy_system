# data_redundancy_system




☁  CLOUD COMPUTING PROJECT
Data Redundancy Removal System

Complete Technical Documentation & Implementation Report



Prepared by: Ajay Kumar
Role: DevOps Engineer  
Date: June 13, 2026



STATUS: ✔  SUCCESSFULLY COMPLETED
 
1. Executive Summary
This document presents the complete design, development, and successful execution of the Data Redundancy Removal System — a cloud computing task completed as part of the Cloud Computing Task List (Task 1). The system was built using Python and SQLite to simulate a real cloud database environment, demonstrating industry-standard techniques for data deduplication, validation, and storage efficiency.

✔  Task Successfully Completed — Key Results at a Glance
  Total Records Processed    :   10
  Unique Records Stored       :    5  (50%)
  Duplicate Records Rejected  :    2  (20%)
  Invalid Records Rejected    :    3  (30%)
  Cloud Storage Efficiency    :   50% reduction achieved
  System Components Built     :    5 Python modules + 3 database tables

 
2. What Is This System? — Plain English Explanation
Imagine a company is collecting customer or business data from many sources — forms, APIs, sensors, or manual entries. Without any control system, the same data gets stored multiple times (duplicates), and invalid or garbage data gets stored too. This wastes storage, causes reporting errors, and increases cloud costs.

The Data Redundancy Removal System solves this problem by acting as a smart gatekeeper before any data reaches the cloud database:

Without This System ✗	With This System ✔
Same record stored 10 times	Same record stored only once
Invalid emails & names saved	Invalid data rejected before storage
Database bloats with garbage	Only clean, verified data stored
Wasted cloud storage & money	Efficient, accurate cloud storage
No audit trail of rejections	Full log of every rejected record

 
3. System Architecture & Data Flow
The system is structured as a 5-module Python pipeline. Each module has a single, clear responsibility. This follows the software engineering principle of Separation of Concerns — each file does one job and does it well.

3.1 Data Flow Diagram
 
  [Incoming Raw Data]
         |
         v
  +-----------------+
  |   validator.py  |  <-- Step 1: Check name, email, category, value
  +-----------------+
         |
    Valid?  No  ---->  [rejected_records table]  (reason: INVALID)
         |
        Yes
         v
  +----------------------+
  | duplicate_checker.py |  <-- Step 2: Generate SHA-256 hash, check DB
  +----------------------+
         |
   Unique?  No  ---->  [rejected_records table]  (reason: DUPLICATE)
         |
        Yes
         v
  +------------------+
  | cloud_storage.py |  <-- Step 3: Write to cloud_records table
  +------------------+
         |
         v
  [cloud_records DB] + [audit_log DB]
 

3.2 Project File Structure
File	Purpose
main.py	Entry point — drives the pipeline, prints all results and summary tables
database.py	Creates the 3 SQLite tables (cloud_records, rejected_records, audit_log)
validator.py	Validates each record — checks name, email format, category, and value
duplicate_checker.py	Generates SHA-256 hash, checks if record already exists in DB
cloud_storage.py	Stores unique verified records; logs rejections and audit entries

 
4. Detailed Code Explanation — Every File, Every Step
4.1  database.py — The Database Foundation
This file creates and manages the SQLite database. It runs first (init_db()) to set up all the tables before any data processing begins. Think of it as building the filing cabinet before you start putting files in it.

What the 3 Tables Do:
Table Name	What It Stores	Why It Exists
cloud_records	Only unique, valid data records	This is the clean cloud database — only good data lives here
rejected_records	All duplicates + invalid entries	Audit trail — so we know what was rejected and why
audit_log	Every action (stored, duplicate, invalid)	Full history for compliance and debugging

Key Code Concept — data_hash UNIQUE Constraint:
data_hash   TEXT NOT NULL UNIQUE   -- SHA256 hash for dedup
The UNIQUE keyword on data_hash is a database-level safeguard. Even if the application code misses a duplicate, the database itself will refuse to store it. This is called defense in depth — multiple layers of protection.

4.2  validator.py — The Data Quality Guardian
This module acts as the first gatekeeper. Before a record gets anywhere near the database, it must pass 4 validation checks. If any check fails, the record is immediately rejected with a clear human-readable reason.

Check	Rule Applied	Example PASS	Example FAIL
Name	Min 2 chars, letters/spaces/hyphens only	"Ajay Kumar"	"   " or "Admin123"
Email	Must match standard email pattern	"ajay@zaltix.com"	"invalid-email"
Category	Must be in approved list of 5 categories	"technology"	"unknown"
Value	Must be numeric and non-negative	"4500.00"	"-50"

Key Code Concept — Regular Expression for Email:
email_regex = r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$'
if not re.match(email_regex, email):
    return False, f"Invalid email format: '{email}'"
A regular expression (regex) is a pattern-matching rule. This specific pattern means: start with letters/numbers/dots/plusses/hyphens, then an @ symbol, then a domain name, then a dot, then a 2+ letter extension. Anything not matching this exact pattern is rejected.

4.3  duplicate_checker.py — The Fingerprinting Engine
This is the heart of the deduplication system. It creates a unique digital fingerprint (hash) for every record, then checks if that fingerprint already exists in the database. This approach is both faster and more reliable than comparing every field one by one.

How SHA-256 Hashing Works:
# Step 1: Normalize the record (lowercase, strip whitespace)
normalized = {
    'name':     record['name'].strip().lower(),
    'email':    record['email'].strip().lower(),
    'category': record['category'].strip().lower(),
    'value':    str(record['value']).strip()
}
 
# Step 2: Convert to a consistent string
record_str = json.dumps(normalized, sort_keys=True)
 
# Step 3: Generate SHA-256 hash (64-character fingerprint)
return hashlib.sha256(record_str.encode()).hexdigest()
 
# Example: 'Ajay Kumar' + 'ajay@zaltix.com' + 'technology' + '4500.0'
#       => '51c336321022ab7d92f3c4e1ab8d6f7e...' (always same result)

Why SHA-256 Hashing? — Key Advantages
  Speed       : One DB query vs. comparing every field separately
  Reliability : SHA-256 is deterministic — same input ALWAYS produces same hash
  Security    : Industry-standard algorithm used in blockchain, SSL certificates
  Simplicity  : Just one UNIQUE column to check instead of 4 columns

4.4  cloud_storage.py — The Storage Controller
This module combines validation results and duplicate check results to make the final decision: store or reject. It also maintains the audit log for every decision made.

The Decision Logic (store_record function):
def store_record(record):
    data_hash = generate_hash(record)       # Get fingerprint
 
    if is_duplicate(data_hash):             # Already in DB?
        log_rejection(record, 'Duplicate')  # Log the rejection
        return {'status': 'duplicate'}      # Reject it
 
    # If unique: INSERT into cloud_records
    cursor.execute("""
        INSERT INTO cloud_records
        (name, email, data_hash, category, value)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, hash, category, value))
 
    log_audit('STORED', hash, 'New record stored')
    return {'status': 'success'}

4.5  main.py — The Orchestrator
This is the master controller that ties all modules together. It defines the test dataset of 10 records (intentionally containing duplicates and invalid entries), then runs each record through the full pipeline and displays results using color-coded terminal output and formatted tables.

The Processing Loop:
for i, record in enumerate(incoming_data, 1):
 
    # Step A: Validate the record
    is_valid, reason = validate_record(record)
    if not is_valid:
        print(f'  INVALID — {reason}')      # Reject
        results['invalid'] += 1
        continue                             # Skip to next record
 
    # Step B: Check duplicate + store
    result = store_record(record)
 
    if result['status'] == 'success':        # New unique record
        results['stored'] += 1
    elif result['status'] == 'duplicate':    # Already exists
        results['duplicate'] += 1

 
5. Execution Results — Record by Record Analysis
5.1  All 10 Records Processed
#	Name	Email	Category	Value	Result
01	Ajay Kumar	ajay@zaltix.com	technology	4500.00	✔ STORED
02	Priya Sharma	priya@example.com	finance	1200.50	✔ STORED
03	Ravi Reddy	ravi@cloud.io	healthcare	890.00	✔ STORED
04	Ajay Kumar	ajay@zaltix.com	technology	4500.00	⚠ DUPLICATE
05	(blank)	invalid-email	retail	100	✗ INVALID (name)
06	Sneha Patel	sneha@edu.in	education	300.75	✔ STORED
07	Ravi Reddy	ravi@cloud.io	healthcare	890.00	⚠ DUPLICATE
08	Admin123	admin@test.com	unknown	0	✗ INVALID (name+cat)
09	Meena Joshi	meena@retail.com	retail	-50	✗ INVALID (value)
10	Kiran Babu	kiran@finance.net	finance	9999.99	✔ STORED

5.2  Final Cloud Database — 5 Unique Verified Records
ID	Name	Email	Category	Value (Rs.)	Stored At
1	Ajay Kumar	ajay@zaltix.com	technology	4500.00	2026-06-13 17:09:15
2	Priya Sharma	priya@example.com	finance	1200.50	2026-06-13 17:09:15
3	Ravi Reddy	ravi@cloud.io	healthcare	890.00	2026-06-13 17:09:15
4	Sneha Patel	sneha@edu.in	education	300.75	2026-06-13 17:09:15
5	Kiran Babu	kiran@finance.net	finance	9999.99	2026-06-13 17:09:15

5.3  Processing Summary
Status	Count
✔  Successfully Stored	5
⚠  Duplicates Rejected	2
✗  Invalid Records	3
TOTAL Processed	10

 
6. How Every Task Requirement Was Met
Task Requirement	How This System Solves It
Design a system to detect duplicate and false data	SHA-256 hashing in duplicate_checker.py creates a unique fingerprint per record. Validator.py detects false/invalid data using field-by-field rules.
Validate new data against existing cloud records	is_duplicate() in duplicate_checker.py queries the live cloud_records table before every insert. New data is always compared against what already exists.
Prevent duplicate entries in the cloud database	Two-layer protection: (1) Python-level hash check, (2) UNIQUE constraint in the database schema itself. Either layer alone would be sufficient, but both together guarantee zero duplicates.
Store only unique and verified data	Only records that pass BOTH the validator AND the duplicate check reach cloud_records. All others go to rejected_records with a reason.
Improve cloud storage efficiency and accuracy	Result: 10 incoming records reduced to 5 stored records — 50% storage reduction. Every stored record is clean, valid, and unique. Audit logs ensure full traceability.

 
7. Technologies & Tools Used
Technology	Version / Type	Why It Was Used
Python	3.14 (Windows)	Primary programming language — clean syntax, excellent for data processing
SQLite	Built-in	Lightweight cloud database simulator — no server needed, file-based
hashlib	Python stdlib	SHA-256 hashing for duplicate fingerprinting — industry standard
re (regex)	Python stdlib	Email and name pattern validation — precise and efficient
json	Python stdlib	Normalize records to consistent strings before hashing
tabulate	0.10.0	Beautiful formatted tables in terminal output — professional presentation
colorama	0.4.6	Color-coded terminal output (green=stored, red=invalid, yellow=duplicate)

 
8. Step-by-Step: How to Run the System
Prerequisites
•	Python 3.x installed on Windows
•	Command Prompt or PowerShell
•	All 5 .py files in the same folder

Execution Steps
1.	Open PowerShell and navigate to project folder:
cd C:\data_redundancy_system

2.	Install required libraries:
pip install tabulate colorama

3.	Run the system:
python main.py

4.	The system automatically: initializes the DB, processes all 10 records, prints results, and shows all tables.

5.	To re-run fresh (delete the database first):
del cloud_storage.db
python main.py

 
9. Conclusion & Key Learnings
The Data Redundancy Removal System was successfully designed, implemented, and executed. The system demonstrates a production-ready approach to cloud data management — combining validation, deduplication, and storage in a clean, modular architecture.

Key Technical Achievements
•	Built a 5-module Python system with clear separation of responsibilities
•	Implemented SHA-256 hashing for fast, reliable duplicate detection
•	Applied regex-based validation for real-world data quality rules
•	Created a 3-table database schema with audit trail
•	Achieved 50% storage efficiency improvement on test dataset
•	Produced color-coded, tabulated output for professional presentation

Real-World Applicability
This system design is directly applicable to real cloud platforms. In production, the SQLite database would be replaced with AWS RDS, Azure SQL, or Google Cloud SQL. The same Python modules — validator.py, duplicate_checker.py, and cloud_storage.py — would function identically with any SQL-compatible database, making this a highly portable and scalable solution.

Task 1: Data Redundancy Removal System — COMPLETE
  All 5 requirements from the Cloud Computing Task List fulfilled
  System tested with 10 records including edge cases
  Zero false positives: all 5 valid unique records stored correctly
  Zero false negatives: all 5 invalid/duplicate records rejected correctly
  Documentation complete and ready for team review


— Ajay Kumar, DevOps Engineer
                                                                                                               |  June 13, 2026
