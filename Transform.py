import pandas as pd
from io import BytesIO

class Transformer:
    """Simple data cleaning and transformations"""

    def __init__(self, df: pd.DataFrame):
        self.df = df


    def has_column(self, col_name: str) -> bool:
        return col_name in self.df.columns

    def validate_columns(self, required: list[str]) -> None:
        missing = set(required) - set(self.df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")



    def rename_column(self, old_name: str, new_name: str) -> None:
        self.validate_columns([old_name])
        self.df = self.df.rename(columns={old_name: new_name})

    def normalize_columns(self) -> None:
        self.df.columns = (
            self.df.columns
                .str.strip()
                .str.lower()
                .str.replace(" ", "_")
        )



    def drop_duplicates(self, subset: list[str] | None = None) -> None:
        self.df = self.df.drop_duplicates(subset=subset)

    def drop_null_rows(self, subset: list[str] | None = None) -> None:
        self.df = self.df.dropna(subset=subset)

    def fill_nulls(self, column: str, value) -> None:
        self.validate_columns([column])
        self.df[column] = self.df[column].fillna(value)

    def column_min(self, column: str):
        self.validate_columns([column])
        return self.df[column].min()

    def column_max(self, column: str):
        self.validate_columns([column])
        return self.df[column].max()

    def column_mean(self, column: str):
        self.validate_columns([column])
        return self.df[column].mean()
    
    def sort_by(self, columns: list[str], ascending: bool | list[bool] = True) -> None:
        self.validate_columns(columns)
        self.df = self.df.sort_values(by=columns, ascending=ascending)

    def group_by(self, columns: list[str]) -> None:
        self.validate_columns(columns)
        self.df = self.df.groupby(columns)

    '''
        Totals: total_amount = quantity * unit_price

        Margins or profits: profit = revenue - cost

        Date differences: days_since_order = today - order_date

        Ratios / percentages: conversion_rate = orders / visits

        Categorization: category = "High" if amount > 1000 else "Low"
    '''

    