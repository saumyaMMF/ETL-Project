"""Deterministic transformations for ERP outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd

from app.config.settings import CONFIG


@dataclass(frozen=True)
class TransformationResult:
    file_a: pd.DataFrame | None = None
    file_b: pd.DataFrame | None = None
    file_c: pd.DataFrame | None = None
    cancellations: pd.DataFrame | None = None


class Transformer:
    def build_file_a(self, df: pd.DataFrame) -> pd.DataFrame:
        output = pd.DataFrame()
        output["Greek Description"] = df["Col B"].astype(str) + " " + df["Col J"].astype(str) + " " + df["Col H"].astype(str)
        output["English Description"] = df["Col I"]
        output["Units"] = "ΤΕΜ"
        output["VAT Category"] = "1"
        output["Supplier Item Code"] = df["Col D"]
        output["House"] = CONFIG.house
        output["Collection Category"] = CONFIG.collection_category
        output["Basic Supplier Code"] = CONFIG.basic_supplier_code
        output["Pricelist Season"] = CONFIG.pricelist_season
        output["Currency"] = "EUR"
        return output

    def build_file_b(self, df: pd.DataFrame) -> pd.DataFrame:
        output = pd.DataFrame()
        output["Supplier Item Code"] = df["Col D"]
        output["House"] = CONFIG.house
        output["Pricelist Season"] = CONFIG.pricelist_season
        output["Collection Code"] = CONFIG.collection_code
        output["Color Code"] = df["Col J"]
        output["Color Description"] = df["Col K"]
        output["Size Code"] = df.apply(self._size_code, axis=1)
        output["Size Description"] = df.apply(self._size_description, axis=1)
        return output

    def build_file_c(self, df: pd.DataFrame) -> pd.DataFrame:
        output = pd.DataFrame()
        output["Supplier Item Code"] = df["Col D"]
        output["House"] = CONFIG.house
        output["Color Code"] = df["Col J"]
        output["Size Code"] = df.apply(self._size_code, axis=1)
        output["Barcode"] = df["Col P"].fillna(df["Col Q"])
        output["Barcode Type"] = df.apply(self._barcode_type, axis=1)
        return output

    def build_order_confirmations(self, df: pd.DataFrame) -> pd.DataFrame:
        output = pd.DataFrame()
        output["Basic Supplier Code"] = CONFIG.basic_supplier_code
        output["Storage Space"] = "001"
        output["Delivery Number"] = df["Col AD"]
        output["Supplier Item Code"] = df["Col J"].astype(str) + df["Col K"].astype(str)
        output["House"] = CONFIG.house
        output["Season"] = CONFIG.pricelist_season
        output["Collection Code"] = CONFIG.collection_code
        output["Quantity"] = df["Col Q"]
        output["Unit Price"] = df["Col AH"].astype(str).str.replace(".", ",", regex=False)
        output["Date 1"] = CONFIG.date_1
        output["Date 2"] = CONFIG.date_2
        output["Date 3"] = CONFIG.date_3
        return output

    def _size_code(self, row: pd.Series) -> str:
        drop = row.get("Col N")
        size_desc = row.get("Col O")
        if drop == "N":
            return str(size_desc)
        return f"{size_desc}/{drop}"

    def _size_description(self, row: pd.Series) -> str:
        drop = row.get("Col N")
        size_desc = str(row.get("Col O"))
        if drop == "N":
            return size_desc
        if "/" in size_desc:
            left, right = size_desc.split("/", maxsplit=1)
            suffix = "2" if drop == "2" else "3"
            return f"{left}/{suffix}{right}"
        return size_desc

    def _barcode_type(self, row: pd.Series) -> str:
        if pd.notna(row.get("Col P")):
            return "1"
        return "2"

    def transform_items(self, df: pd.DataFrame) -> TransformationResult:
        return TransformationResult(
            file_a=self.build_file_a(df),
            file_b=self.build_file_b(df),
            file_c=self.build_file_c(df),
        )

    def transform_changes(self, df: pd.DataFrame) -> TransformationResult:
        cancellations = df[df["Status"] == "ΑΚΥΡΟ"] if "Status" in df.columns else pd.DataFrame()
        return TransformationResult(cancellations=cancellations)

    def transform_order_confirmations(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.build_order_confirmations(df)
