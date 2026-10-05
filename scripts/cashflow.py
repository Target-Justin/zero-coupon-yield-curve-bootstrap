import pandas as pd
import QuantLib as ql

from config import NOMINAL, SCHEDULE_CALENDAR, SETTLEMENT_CALENDAR, SETTLEMENT_DAYS
from scripts.utils.utils import to_pd_date, to_ql_date

def generate_cashflows(bonds_df : pd.DataFrame) -> pd.DataFrame:
    """Generate the future coupon and principal cash flows of each bond.

    Only cash flows strictly after the settlement date are kept, since a coupon
    paid on the settlement date belongs to the seller. The principal is added to
    the last cash flow. The evaluation date is read from the first row.

    Args:
    bonds_df: DataFrame with one row per bond and the columns Bond, Maturity,
    EvaluationDate, AccrualStartDate, Frequency (coupons per year), Coupon
    (annual rate as a decimal) and DayCount.

    Returns:
    DataFrame with the columns Bond, Date and Cashflow (per NOMINAL), one row
    per future cash flow.

    Raises:
    ValueError: If a bond has no cash flow after the settlement date.
    """

    cashflows = []

    evaluation = to_ql_date(bonds_df["EvaluationDate"].iloc[0])
    settlement = SETTLEMENT_CALENDAR.advance(evaluation, SETTLEMENT_DAYS, ql.Days)

    for row in bonds_df.itertuples():

        bond = row.Bond

        maturity = to_ql_date(row.Maturity)
        accrual_start_date = to_ql_date(row.AccrualStartDate)

        frequency = row.Frequency
        months_per_period = 12 // frequency

        coupon = row.Coupon
        coupon_amount = NOMINAL * coupon / frequency

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                                SCHEDULE_CALENDAR, ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, False)

        future_dates = [date for date in schedule if date > settlement]

        if not future_dates:
            raise ValueError(f"{bond} has no cashflow after the settlement date {settlement}.")

        final_date = future_dates[-1]
        
        for date in future_dates:

            cashflow = coupon_amount

            if date == final_date:
                cashflow += NOMINAL

            cashflows.append({"Bond" : bond, "Date" : to_pd_date(date), "Cashflow" : cashflow})

    return pd.DataFrame(cashflows)