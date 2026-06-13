import re

VALID_CATEGORIES = {"finance", "healthcare", "education", "technology", "retail"}

def validate_record(record: dict) -> tuple[bool, str]:
    """
    Validate a data record before storing.
    Returns (is_valid: bool, reason: str)
    """
    # --- Name check ---
    name = record.get("name", "").strip()
    if not name or len(name) < 2:
        return False, "Invalid or missing name (min 2 chars)"

    if not re.match(r"^[A-Za-z\s\-']+$", name):
        return False, f"Name contains invalid characters: '{name}'"

    # --- Email check ---
    email = record.get("email", "").strip()
    email_regex = r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_regex, email):
        return False, f"Invalid email format: '{email}'"

    # --- Category check ---
    category = record.get("category", "").strip().lower()
    if category not in VALID_CATEGORIES:
        return False, f"Unknown category '{category}'. Allowed: {VALID_CATEGORIES}"

    # --- Value check ---
    try:
        value = float(record.get("value", 0))
        if value < 0:
            return False, f"Value cannot be negative: {value}"
    except (ValueError, TypeError):
        return False, f"Value must be numeric: {record.get('value')}"

    return True, "Valid"