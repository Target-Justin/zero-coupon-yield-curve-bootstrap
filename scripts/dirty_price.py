import pandas as pd
import QuantLib as ql

from config import NOMINAL, SCHEDULE_CALENDAR, SETTLEMENT_CALENDAR, SETTLEMENT_DAYS
from scripts.utils.utils import to_pd_date, to_ql_date, get_day_counter

def generate_dirty_prices(bonds_df : pd.DataFrame) -> pd.DataFrame:
    """Calculate the dirty price of each bond from its clean price.

    The dirty price is the clean price plus the interest accrued between the
    previous coupon date and the settlement date, computed with the day-count
    convention of the bond.

    Args:
        bonds_df: DataFrame with one row per bond and the columns Bond, Maturity,
            EvaluationDate, AccrualStartDate, Frequency (coupons per year), Coupon
            (annual rate as a decimal), CleanPrice (in the same unit as NOMINAL)
            and DayCount.

    Returns:
        DataFrame with the columns Bond, Maturity and DirtyPrice.
    """
    
    dirty_prices = []

    for row in bonds_df.itertuples():

        bond = row.Bond

        maturity = to_ql_date(row.Maturity)
        evaluation = to_ql_date(row.EvaluationDate)
        accrual_start_date = to_ql_date(row.AccrualStartDate)
        settlement = SETTLEMENT_CALENDAR.advance(evaluation, SETTLEMENT_DAYS, ql.Days)

        frequency = row.Frequency
        months_per_period = 12 // frequency

        coupon = row.Coupon
        coupon_amount = NOMINAL * coupon / frequency

        clean_price = row.CleanPrice

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                                SCHEDULE_CALENDAR, ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, False)

        previous_coupon = None
        next_coupon = None

        for date in schedule:

            if date <= settlement:

                previous_coupon = date

            else:

                next_coupon = date

                break

        day_count = get_day_counter(row.DayCount)

        accrued_interest = 0

        if previous_coupon is not None and next_coupon is not None:

            elapsed_time = day_count.yearFraction(previous_coupon, settlement)

            period_length = day_count.yearFraction(previous_coupon, next_coupon)

            accrued_fraction = elapsed_time / period_length

            accrued_interest = coupon_amount*accrued_fraction

        dirty_price = clean_price + accrued_interest

        dirty_prices.append({"Bond": bond, "Maturity": to_pd_date(maturity), "DirtyPrice": dirty_price})

    return pd.DataFrame(dirty_prices)