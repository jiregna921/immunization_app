from config.thresholds import VACCINE_THRESHOLDS

def categorize_utilization(row):
    antigen = row["Antigen"]
    rate = row["Utilization Rate"] / 100  # Convert % to 0-1

    thresholds = VACCINE_THRESHOLDS.get(antigen)

    if not thresholds:
        # Default fallback
        if rate > 1.0:
            return "Unacceptable (>100%)"
        elif rate >= 0.80:
            return "Acceptable (80–100%)"
        else:
            return "Low Utilization (<80%)"

    if rate > thresholds["unacceptable"]:
        return "Unacceptable (>100%)"
    elif thresholds["acceptable"] <= rate <= thresholds["unacceptable"]:
        return "Acceptable (80–100%)"
    else:
        return "Low Utilization (<80%)"
