"""Cancellation logic for change files."""

import pandas as pd

from app.config.settings import CONFIG


def build_cancellation_file(df: pd.DataFrame) -> pd.DataFrame:
    output = pd.DataFrame()
    output["Supplier Item Code"] = df["Col F"]
    output["Color Code"] = CONFIG.color_prefix + "/" + df["Col G"].astype(str)
    output["Pricelist Season"] = CONFIG.pricelist_season
    output["Collection Code"] = CONFIG.collection_code
    output["House"] = CONFIG.house
    return output
