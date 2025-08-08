import pandas as pd

def load_dataset(file_path_or_buffer) -> pd.DataFrame:
    # Load file
    if isinstance(file_path_or_buffer, str) and file_path_or_buffer.endswith(".xlsx"):
        df = pd.read_excel(file_path_or_buffer)
    else:
        df = pd.read_csv(file_path_or_buffer)

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()                       # remove leading/trailing spaces
        .str.replace("\u00A0", " ")        # replace non-breaking spaces
        .str.replace("Received", "Distributed", regex=False)
    )

    return df
