import pandas as pd
import QuantLib as ql

from config import NOMINAL, CALENDAR_SCHEDULE_CONVENTIONS, SETTLEMENT_CALENDAR_CONVENTIONS, SETTLEMENT_DAYS_CONVENTIONS, DATE_GENERATION_CONVENTIONS, BUSINESS_DAY_CONVENTIONS, END_OF_MONTH_CONVENTIONS
from scripts.common.common import to_pd_date, to_ql_date

def generate_cashflows(bonds_df : pd.DataFrame) -> pd.DataFrame:
    """Generate the future coupon and principal cash flows of each bond.

    The coupon schedule runs backward from the maturity to the accrual start date, with
    unadjusted dates. Only the payment dates after settlement (evaluation date + 2 TARGET
    business days) are kept. Each coupon is NOMINAL × coupon / frequency, and the nominal
    is added on the last date.

    Args:
        bonds_df: DataFrame containing the bond information (Bond, Maturity, EvaluationDate,
                  AccrualStartDate, Frequency, Coupon).

    Returns:
        DataFrame with the columns Bond, Date and Cashflow, one row per payment.
    """

    cashflows = []

    for row in bonds_df.itertuples():

        bond = row.Bond

        maturity = to_ql_date(row.Maturity)
        evaluation = to_ql_date(row.EvaluationDate)
        accrual_start_date = to_ql_date(row.AccrualStartDate)
        settlement = SETTLEMENT_CALENDAR_CONVENTIONS["OAT"].advance(evaluation, SETTLEMENT_DAYS_CONVENTIONS["OAT"], ql.Days)

        frequency = row.Frequency
        months_per_period = 12 // frequency

        coupon = row.Coupon
        coupon_amount = NOMINAL * coupon / frequency

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                               CALENDAR_SCHEDULE_CONVENTIONS["OAT"], BUSINESS_DAY_CONVENTIONS["OAT"], 
                               BUSINESS_DAY_CONVENTIONS["OAT"], DATE_GENERATION_CONVENTIONS["OAT"], 
                               END_OF_MONTH_CONVENTIONS["OAT"])

        future_dates = [date for date in schedule if date > settlement]
        final_date = future_dates[-1] if future_dates else None
        
        for date in future_dates:

            cashflow = coupon_amount

            if date == final_date:
                cashflow += NOMINAL

            cashflows.append({"Bond" : bond, "Date" : to_pd_date(date), "Cashflow" : cashflow})

    return pd.DataFrame(cashflows)