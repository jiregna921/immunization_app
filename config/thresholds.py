# File: C:\Users\Sagni\Desktop\immunization_app\config\thresholds.py

# This file should NOT have any "import" statements.

# Threshold configuration for each vaccine
VACCINE_THRESHOLDS = {
    "BCG": {
        "unacceptable": 1.00,  # >100%
        "acceptable": 0.50,    # >50% to 100%
    },
    "IPV": {
        "unacceptable": 1.00,  # >100%
        "acceptable": 0.90,    # >90% to 100%
    },
    "Measles": {
        "unacceptable": 1.00,
        "acceptable": 0.65,
    },
    "Penta": {
        "unacceptable": 1.00,
        "acceptable": 0.95,
    },
    "Rota": {
        "unacceptable": 1.00,
        "acceptable": 0.90,
    }
}

DEFAULT_THRESHOLDS = {
    "unacceptable": 1.00,
    "acceptable": 0.80,
}

def categorize_utilization(row):
    """
    Categorizes the utilization rate based on the specific vaccine's thresholds.
    """
    antigen = row.get("Antigen")
    # Utilization Rate is a percentage, so divide by 100
    utilization_rate = row.get("Utilization Rate", 0) / 100.0

    # This function accesses VACCINE_THRESHOLDS, which is defined in this same file.
    thresholds = VACCINE_THRESHOLDS.get(antigen, DEFAULT_THRESHOLDS)

    unacceptable_threshold = thresholds["unacceptable"]
    acceptable_threshold = thresholds["acceptable"]

    if utilization_rate > unacceptable_threshold:
        return "Unacceptable (>100%)"
    elif utilization_rate >= acceptable_threshold:
        return f"Acceptable ({int(acceptable_threshold*100)}–100%)"
    else:
        return f"Low Utilization (<{int(acceptable_threshold*100)}%)"