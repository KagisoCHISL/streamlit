# Transformer Class – Function Blueprint

This document defines the **functions your Transformer class should expose**.
You can implement them however you want — this is the **contract**, not the code.

The Transformer:
- Has **no UI**
- Has **no SharePoint knowledge**
- Works purely with **in-memory data**

---

## 1. Load & Normalize Input

### `from_excel(content: bytes) -> DataFrame`

**Purpose**
- Read an Excel file from memory
- Return a pandas DataFrame

**Responsibilities**
- Load default sheet (or first sheet)
- Strip whitespace from column names
- Normalize column casing (optional)

---

## 2. Validate Required Columns

### `validate_columns(df: DataFrame, required: list[str]) -> None`

**Purpose**
- Ensure required columns exist before processing

**Responsibilities**
- Raise a clear error if columns are missing
- Fail fast before transformations

---

## 3. Basic Data Cleaning

### `clean(df: DataFrame) -> DataFrame`

**Purpose**
- Apply generic data-cleaning rules

**Typical Operations**
- Drop duplicates
- Handle missing values
- Trim string columns
- Cast numeric/date types

---

## 4. Business Transformations

### `transform(df: DataFrame, config: dict) -> DataFrame`

**Purpose**
- Apply business-specific logic

**Examples**
- Create calculated columns
- Scale or normalize values
- Categorize rows
- Conditional transformations

**Notes**
- Should be config-driven
- No hard-coded UI assumptions

---

## 5. Filtering Rules

### `filter(df: DataFrame, rules: dict) -> DataFrame`

**Purpose**
- Remove or keep rows based on conditions

**Examples**
- Remove rows below a threshold
- Keep only specific categories
- Date-based filtering

---

## 6. Aggregations (Optional)

### `aggregate(df: DataFrame, group_by: list[str], metrics: dict) -> DataFrame`

**Purpose**
- Group and summarize data

**Examples**
- Totals per category
- Monthly averages
- Count of records

---

## 7. Output Validation

### `validate_output(df: DataFrame) -> list[str]`

**Purpose**
- Validate final output before upload

**Returns**
- List of warnings (empty list if OK)

**Examples**
- Empty DataFrame
- Unexpected value ranges
- Negative totals

---

## 8. Export to Excel (Bytes)

### `to_excel_bytes(df: DataFrame) -> bytes`

**Purpose**
- Convert DataFrame back to Excel bytes

**Responsibilities**
- Write to memory buffer
- Return raw bytes (no file I/O)

---

## Minimal Transformer Interface (Summary)

