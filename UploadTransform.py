import streamlit as st
import pandas as pd
import numpy as np
from Transform import Transformer


st.title("FILE TRANSFORMER")

st.write(
    "Select an Excel or CSV file from your computer to preview its contents, "
    "and view dirtiness statistics, possibly clean it."
)

uploaded_file = st.file_uploader("Upload file", type=["xlsx", "csv"])

if uploaded_file:
    st.write("Uploaded file:", uploaded_file.name)

    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    transformer = Transformer(df)

    st.sidebar.title("Sorting Options")
    sorting_col = st.sidebar.selectbox("Select Column to sort", [""] + list(transformer.df.columns))
    if sorting_col != "":
        sort_order = st.sidebar.radio("Sort Order", ["Ascending", "Descending"])
        ascending = sort_order == "Ascending"
        transformer.sort_by([sorting_col], ascending=ascending)

    st.sidebar.title("Column Operations")

    if st.sidebar.checkbox("Normalize Column Names"):
        transformer.normalize_columns()

    if st.sidebar.checkbox("Rename a Column"):
        old_name = st.sidebar.selectbox("Select column to rename", transformer.df.columns)
        new_name = st.sidebar.text_input("New column name", "")
        if new_name:
            transformer.rename_column(old_name, new_name)

    if st.sidebar.checkbox("Drop Duplicates"):
        subset = st.sidebar.multiselect("Columns to consider", transformer.df.columns)
        subset = subset if subset else None
        transformer.drop_duplicates(subset=subset)

    if st.sidebar.checkbox("Drop Rows with Nulls"):
        subset = st.sidebar.multiselect("Columns to check for nulls", transformer.df.columns)
        subset = subset if subset else None
        transformer.drop_null_rows(subset=subset)

    if st.sidebar.checkbox("Fill Null Values"):
        column = st.sidebar.selectbox("Select column to fill nulls", transformer.df.columns)
        value = st.sidebar.text_input("Value to fill", "")
        if value != "":
            try:
                value = float(value)
            except ValueError:
                pass
            transformer.fill_nulls(column, value)

    st.write("### File Preview (Transformed/Sorted)")
    st.dataframe(transformer.df)

    def dirtiness_stats(df: pd.DataFrame) -> pd.DataFrame:
        stats_df = pd.DataFrame(index=df.columns, columns=[
            "Null Values", "Unexpected Data Types", "Out-of-Range Values"
        ])
        for col in df.columns:
            null_percentage = df[col].isna().mean() * 100

            if np.issubdtype(df[col].dtype, np.number):
                unexpected_data_type_percentage = df[col].apply(
                    lambda x: not isinstance(x, (int, float)) and not pd.isna(x)
                ).mean() * 100
                out_of_range_percentage = ((df[col] < 0) | (df[col] > 100)).mean() * 100
            else:
                unexpected_data_type_percentage = 0
                out_of_range_percentage = 0

            stats_df.loc[col, "Null Values"] = round(null_percentage, 1)
            stats_df.loc[col, "Unexpected Data Types"] = round(unexpected_data_type_percentage, 1)
            stats_df.loc[col, "Out-of-Range Values"] = round(out_of_range_percentage, 1)

        return stats_df

    stats_df = dirtiness_stats(transformer.df)

    st.write("### File Dirtiness Statistics")
    st.dataframe(stats_df)