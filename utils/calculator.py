# utils/calculator.py

import pandas as pd
from config.thresholds import VACCINE_THRESHOLDS

def calculate_utilization_and_category(df: pd.DataFrame) -> pd.DataFrame:
    result_df = df.copy()

    # Loop over each vaccine in the threshold config
    for vaccine in VACCINE_THRESHOLDS.keys():
        distributed_col = f"{vaccine} Distributed"
        administered_col = f"{vaccine} Administered"
        usage_col = f"{vaccine} Usage Rate"
        category_col = f"{vaccine} Category"

        # Avoid division by zero
        result_df[usage_col] = result_df.apply(
            lambda row: row[administered_col] / row[distributed_col]
            if row[distributed_col] > 0 else 0,
            axis=1
        )

        # Apply categorization based on thresholds
        result_df[category_col] = result_df[usage_col].apply(
            lambda rate: categorize_vaccine_utilization(vaccine, rate)
        )

    return result_df


def categorize_vaccine_utilization(vaccine: str, rate: float) -> str:
    thresholds = VACCINE_THRESHOLDS[vaccine]

    if rate > thresholds["unacceptable"]:
        return "Unacceptable"
    elif rate > thresholds["acceptable"]:
        return "Acceptable"
    else:
        return "Low Utilization"
