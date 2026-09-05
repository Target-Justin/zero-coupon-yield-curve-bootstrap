import pandas as pd
import QuantLib as ql
from decimal import Decimal

def to_ql_date(date):
    return ql.Date(date.day, date.month, date.year)

def to_pd_date(date):
    return pd.Timestamp(date.year(), date.month(), date.dayOfMonth())

def generate_cashflows(bonds_df : pd.DataFrame, nominal : Decimal = Decimal("100.0")) -> pd.DataFrame:
    """Generate future coupon and principal cash flows for each bond.

    Args:
        bonds_df: DataFrame containing bond information.
        nominal: Nominal value of each bond.

    Returns:
        DataFrame containing the bond cash flows and payment dates.
    """    

    cashflows = []

    calendar = ql.NullCalendar()

    for row in bonds_df.itertuples():

        maturity = to_ql_date(row.Maturity)
        evaluation = to_ql_date(row.EvaluationDate)
        accrual_start_date = to_ql_date(row.AccrualStartDate)
        frequency = row.Frequency
        bond = row.Bond
        months_per_period = 12//frequency
        coupon = Decimal(str(row.Coupon))
        coupon_amount = nominal * coupon / Decimal(frequency)

        settlement = calendar.advance(evaluation, 2, ql.Days)

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                               calendar, ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, False)

        future_dates = [date for date in schedule if date > settlement]
        final_date = future_dates[-1] if future_dates else None
        
        for date in future_dates:

            cashflow = coupon_amount

            if date == final_date:
                cashflow += nominal

            cashflows.append({"Bond" : bond, "Date" : to_pd_date(date), "Cashflow" : cashflow})

    return pd.DataFrame(cashflows)