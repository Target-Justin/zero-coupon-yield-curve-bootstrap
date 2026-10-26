import pandas as pd
import QuantLib as ql

from scripts.common.common import to_pd_date, get_day_counter
from config import NOMINAL, TENOR_UNITS, CALENDAR_SCHEDULE_CONVENTIONS, DATE_GENERATION_CONVENTIONS, BUSINESS_DAY_CONVENTIONS, PAYMENT_PERIOD_CONVENTIONS, END_OF_MONTH_CONVENTIONS

def generate_cashflows(mid_df : pd.DataFrame, settlement_date : ql.Date, reference_rate : str) -> pd.DataFrame:
    """Generate the fixed-leg cash flows of each OIS.

    Each swap is treated as a par bond: it pays NOMINAL * Mid * year fraction at the end of each
    annual period (a single period up to one year) and repays the nominal at maturity.
    The schedule is generated forward from the settlement date, so the last period can be
    shorter than a year (18-month swap).

    Args:
        mid_df: DataFrame containing the OIS mid rates (decimal), as returned by generate_mid.
        settlement_date: Settlement date, start of every swap.
        reference_rate: Reference rate of the OIS (ESTR or SOFR), which selects the calendar.

    Returns:
        DataFrame with the columns Ticker, Cashflow, StartDate, PaymentDate and AccrualFraction
        (year fraction of the period), one row per payment.
    """

    cashflows = []

    calendar = CALENDAR_SCHEDULE_CONVENTIONS[reference_rate]

    for row in mid_df.itertuples():

        ticker = row.Ticker 
        time_unit = TENOR_UNITS[row.Unit]
        term = int(row.Term)
        mid = row.Mid

        maturity = calendar.advance(settlement_date, term, time_unit, ql.ModifiedFollowing)
        day_count = get_day_counter(row.Daycount)

        schedule = ql.Schedule(settlement_date, maturity, PAYMENT_PERIOD_CONVENTIONS["OIS"], calendar, BUSINESS_DAY_CONVENTIONS["OIS"],
                             BUSINESS_DAY_CONVENTIONS["OIS"], DATE_GENERATION_CONVENTIONS["OIS"], END_OF_MONTH_CONVENTIONS["OIS"])

        dates = list(schedule)
        final_date = dates[-1]
        periods = list(zip(dates[:-1], dates[1:]))

        for start_date, payment_date in periods:

            accrual_fraction = day_count.yearFraction(start_date, payment_date)

            if payment_date == final_date:

                cashflow = NOMINAL * mid * accrual_fraction + NOMINAL

            else:

                cashflow = NOMINAL * mid * accrual_fraction

            cashflows.append({"Ticker" : ticker, "Cashflow" : cashflow, "StartDate" : to_pd_date(start_date), "PaymentDate" : to_pd_date(payment_date), "AccrualFraction" : accrual_fraction})

    return pd.DataFrame(cashflows)