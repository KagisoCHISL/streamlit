import streamlit as st
import pandas as pd
import numpy as np
from Transform import Transformer
import matplotlib.pyplot as plt
import seaborn as sns


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
    
    def generate_chart(df: pd.DataFrame, x_var: str, y_var: list[str], plot_type: str, sort_x: bool = True) -> None:

        plot_df = df.copy()


        if np.issubdtype(plot_df[x_var].dtype, np.object_) or np.issubdtype(plot_df[x_var].dtype, np.str_):
            try:
                plot_df[x_var] = pd.to_datetime(plot_df[x_var])
            except Exception:
                pass  


        if sort_x:
            plot_df = plot_df.sort_values(by=x_var)

        plt.figure(figsize=(10,6))

        if plot_type == "line":
            for y in y_var:
                plt.plot(plot_df[x_var], plot_df[y], marker='o', label=y)
            plt.xlabel(x_var)
            plt.ylabel(", ".join(y_var))
            plt.title("Line Plot")
            plt.legend()
            plt.grid(True)

        elif plot_type == "bar":
            for y in y_var:
                plt.bar(plot_df[x_var], plot_df[y], label=y)
            plt.xlabel(x_var)
            plt.ylabel(", ".join(y_var))
            plt.title("Bar Plot")
            plt.legend()

        elif plot_type == "scatter":
            for y in y_var:
                plt.scatter(plot_df[x_var], plot_df[y], label=y)
            plt.xlabel(x_var)
            plt.ylabel(", ".join(y_var))
            plt.title("Scatter Plot")
            plt.legend()
            plt.grid(True)

        elif plot_type == "hist":
            for y in y_var:
                plt.hist(plot_df[y], alpha=0.5, label=y)
            plt.xlabel("Value")
            plt.ylabel("Frequency")
            plt.title("Histogram")
            plt.legend()

        elif plot_type == "box":
            sns.boxplot(data=plot_df[y_var])
            plt.title("Box Plot")

        elif plot_type == "area":
            plot_df.set_index(x_var)[y_var].plot.area()
            plt.xlabel(x_var)
            plt.ylabel(", ".join(y_var))
            plt.title("Area Plot")

        elif plot_type == "pie":
            if len(y_var) != 1:
                raise ValueError("Pie plot only supports a single y variable")
            plt.pie(plot_df[y_var[0]], labels=plot_df[x_var], autopct='%1.1f%%')
            plt.title("Pie Chart")

        else:
            raise ValueError(f"Plot type '{plot_type}' not recognized")

        plt.xticks(rotation=45)
        plt.tight_layout()


        stats_df = dirtiness_stats(transformer.df)

        st.write("### File Dirtiness Statistics")
        st.dataframe(stats_df)

    if st.checkbox("Graph Data."):
        st.write("Select a plot type to visualize:")
        plot_type = st.radio(
            "Plot Type",
            ["bar", "line", "scatter", "hist", "box", "area", "pie"]
        )
        

        numeric_cols = transformer.df.select_dtypes(include=np.number).columns.tolist()
        
        if numeric_cols:
            x_var = st.selectbox("Select X-axis variable", numeric_cols)
            y_vars = st.multiselect("Select Y-axis variable(s)", numeric_cols, default=numeric_cols)
            
            if st.button("Generate Plot"):
                try:
                    generate_chart(transformer.df, x_var, y_vars, plot_type)
                    st.pyplot(plt.gcf()) 
                except Exception as e:
                    st.error(f"Error generating plot: {e}")
        else:
            st.warning("No numeric columns available for plotting.")

    st.write("### Export Transformed File")

    # Option to select file type
    file_type = st.radio("Select file type to export", ["CSV", "Excel"])

    if file_type == "CSV":
        csv_data = transformer.df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"{uploaded_file.name.split('.')[0]}_transformed.csv",
            mime="text/csv"
        )
    elif file_type == "Excel":
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            transformer.df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_data = output.getvalue()
        
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=f"{uploaded_file.name.split('.')[0]}_transformed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
