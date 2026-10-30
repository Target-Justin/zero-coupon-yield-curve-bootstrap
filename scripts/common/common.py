import io
import pandas as pd
import QuantLib as ql

from pathlib import Path

def to_pd_date(date):
    return pd.Timestamp(date.year(), date.month(), date.dayOfMonth())

def to_ql_date(date):
    return ql.Date(date.day, date.month, date.year)

def get_day_counter(day_count):

    day_count = day_count.upper().replace("-", "/").replace(" ", "")

    if day_count == "ACT/ACT":
        return ql.ActualActual(ql.ActualActual.ISDA)

    elif day_count == "ACT/360":
        return ql.Actual360()

    elif day_count == "ACT/365":
        return ql.Actual365Fixed()

    elif day_count == "30/360":
        return ql.Thirty360(ql.Thirty360.BondBasis)

    else:
        raise ValueError(
            f"Unknown daycount convention : {day_count}"
        )

def log_linear_interpolation(t : float, t_last : float, last_discount_factor : float, t_n : float, x : float) -> float:
    w = (t - t_last)/(t_n - t_last)
    return last_discount_factor * (x / last_discount_factor)**w

def read_csv_robust(path : Path, numeric_columns : tuple = ()) -> pd.DataFrame:

    raw = Path(path).read_bytes()

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")

    lines = text.splitlines()

    if not lines:
        raise ValueError(f"{path}: empty file.")

    sep, decimal = (";", ",") if lines[0].count(";") > lines[0].count(",") else (",", ".")

    dataset = pd.read_csv(io.StringIO(text), sep = sep, decimal = decimal)

    for column in numeric_columns:

        if column not in dataset.columns:
            raise ValueError(f"{path}: missing column {column}. Columns found: {list(dataset.columns)}.")

        if not pd.api.types.is_numeric_dtype(dataset[column]):
            raise ValueError(f"{path}: column {column} is not numeric (first value: {dataset[column].iloc[0]!r}). Check the decimal separator of the file.")

    return dataset

def parse_dates(dates : pd.Series) -> pd.Series:

    for date_format in ("%Y-%m-%d", "%d/%m/%Y"):

        try:
            return pd.to_datetime(dates, format = date_format)

        except ValueError:
            continue

    raise ValueError(f"Column {dates.name}: dates must be written YYYY-MM-DD or DD/MM/YYYY (first value: {dates.iloc[0]!r}).")