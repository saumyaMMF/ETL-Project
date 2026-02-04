"""Cancellation logic for change files."""

import pandas as pd


def build_cancellation_file(df: pd.DataFrame) -> pd.DataFrame:
    output = pd.DataFrame()
    output["Greek Description"] = "ΑΚΥΡΟ"
    output["Supplier Item Code"] = df["Col F"]
    output["Color Code"] = df["Col G"]
    return output
