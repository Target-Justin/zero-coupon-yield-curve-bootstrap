import pandas as pd
import QuantLib as ql

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