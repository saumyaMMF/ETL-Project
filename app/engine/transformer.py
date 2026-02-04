"""Deterministic transformations for ERP outputs."""

from __future__ import annotations

from dataclasses import dataclass
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
        output["English Description"] = df["Col I"]
        output["Subcategory"] = df.apply(self._subcategory, axis=1)
        output["Sex"] = df["Col L"]
        output["Greek Description"] = output.apply(
            lambda row: self._join_fields(row["English Description"], row["Subcategory"], row["Sex"]),
            axis=1,
        )
        output["Units"] = "ΤΕΜ"
        output["VAT Category"] = "1"
        output["Supplier Item Code"] = df["Col D"]
        output["House"] = CONFIG.house
        output["Code Category"] = CONFIG.code_category
        output["Collection Category"] = CONFIG.collection_category
        output["Basic Supplier Code"] = CONFIG.basic_supplier_code
        output["Made In"] = df["Col V"]
        output["Weight"] = df["Col T"].astype(str).str.replace(".", ",", regex=False)
        output["Intrastat Code"] = df["Col R"].astype(str).str.replace(r"\D", "", regex=True).str.slice(0, 8)
        output["Composition"] = df["Col M"]
        output["Pricelist Season"] = CONFIG.pricelist_season
        output["Column W"] = "0"
        output["Currency"] = "EUR"
        output["Sustainable"] = df.apply(self._sustainable, axis=1)
        output["Original Supplier Code"] = df["Col D"]
        return output

    def build_file_b(self, df: pd.DataFrame) -> pd.DataFrame:
        output = pd.DataFrame()
        output["Supplier Item Code"] = df["Col D"]
        output["House"] = CONFIG.house
        output["Code Category"] = CONFIG.code_category
        output["Pricelist Season"] = CONFIG.pricelist_season
        output["Collection Code"] = CONFIG.collection_code
        output["Color Code"] = df["Col J"]
        output["Color Description"] = df["Col K"]
        output["Size Code"] = df.apply(self._size_code, axis=1)
        output["Size Description"] = df.apply(self._size_description, axis=1)
        return output

    def build_file_c(self, df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, row in df.iterrows():
            base = {
                "Supplier Item Code": row.get("Col D"),
                "House": CONFIG.house,
                "Code Category": CONFIG.code_category,
                "Color Code": row.get("Col J"),
                "Size Code": self._size_code(row),
            }
            ean = row.get("Col P")
            upc = row.get("Col Q")
            if pd.notna(ean):
                rows.append({**base, "Barcode": ean, "Barcode Type": "1"})
            if pd.notna(upc):
                rows.append({**base, "Barcode": upc, "Barcode Type": "2"})
        return pd.DataFrame(
            rows,
            columns=[
                "Supplier Item Code",
                "House",
                "Code Category",
                "Color Code",
                "Size Code",
                "Barcode",
                "Barcode Type",
            ],
        )

    def build_order_confirmations(self, df: pd.DataFrame) -> pd.DataFrame:
        output = pd.DataFrame()
        output["Basic Supplier Code"] = CONFIG.basic_supplier_code
        output["Storage Space"] = "001"
        output["Supplier Customer Code"] = df.apply(self._supplier_customer_code, axis=1)
        output["Delivery Number"] = df["Col AD"]
        output["Supplier Item Code"] = df["Col J"].astype(str) + df["Col K"].astype(str)
        output["House"] = CONFIG.house
        output["Code Category"] = CONFIG.code_category
        output["Color"] = df["Col K"]
        output["Size"] = df["Col O"]
        output["Season"] = CONFIG.pricelist_season
        output["Collection Code"] = CONFIG.collection_code
        output["Quantity"] = df["Col Q"]
        output["Unit Price"] = df["Col AH"].astype(str).str.replace(".", ",", regex=False)
        output["Date 1"] = CONFIG.date_1
        output["Date 2"] = CONFIG.date_2
        output["Date 3"] = CONFIG.date_3
        return output

    def _join_fields(self, *values: str) -> str:
        cleaned = [str(value).strip() for value in values if pd.notna(value) and str(value).strip()]
        return " ".join(cleaned)

    def _subcategory(self, row: pd.Series) -> str:
        return self._join_fields(row.get("Col AD"), row.get("Col AG"))

    def _sustainable(self, row: pd.Series) -> str:
        flags = [row.get("Col AI"), row.get("Col AJ")]
        return "1" if any(str(flag).strip().upper() == "Y" for flag in flags if pd.notna(flag)) else "0"

    def _size_code(self, row: pd.Series) -> str:
        drop = row.get("Col N")
        size_desc = row.get("Col O")
        if drop == "N":
            return str(size_desc)
        return f"{size_desc}/{drop}"

    def _size_description(self, row: pd.Series) -> str:
        drop = row.get("Col N")
        size_desc = str(row.get("Col O"))
        if drop == "N" or pd.isna(drop):
            return size_desc
        left = size_desc
        try:
            left_value = int(float(left))
        except ValueError:
            left_value = None
        prefix = "3" if left_value is not None and left_value >= 30 else "2"
        return f"{left}/{prefix}{drop}"

    def _supplier_customer_code(self, row: pd.Series) -> str:
        for column in ("Supplier Customer Code", "Customer Code", "Col H"):
            value = row.get(column)
            if pd.notna(value) and str(value).strip():
                return str(value)
        return ""

    def transform_items(self, df: pd.DataFrame) -> TransformationResult:
        return TransformationResult(
            file_a=self.build_file_a(df),
            file_b=self.build_file_b(df),
            file_c=self.build_file_c(df),
        )

    def transform_changes(self, df: pd.DataFrame) -> TransformationResult:
        filtered = df[df["Status"] == "ΑΚΥΡΟ"] if "Status" in df.columns else df
        cancellations = pd.DataFrame()
        if not filtered.empty:
            cancellations["Supplier Item Code"] = filtered["Col F"]
            cancellations["Color Code"] = CONFIG.color_prefix + "/" + filtered["Col G"].astype(str)
            cancellations["Pricelist Season"] = CONFIG.pricelist_season
            cancellations["Collection Code"] = CONFIG.collection_code
            cancellations["House"] = CONFIG.house
        return TransformationResult(cancellations=cancellations)

    def transform_order_confirmations(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.build_order_confirmations(df)
