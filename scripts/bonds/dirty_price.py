import pandas as pd
import QuantLib as ql

from config import NOMINAL, CALENDAR_SCHEDULE_CONVENTIONS, SETTLEMENT_CALENDAR_CONVENTIONS, SETTLEMENT_DAYS_CONVENTIONS, DATE_GENERATION_CONVENTIONS, BUSINESS_DAY_CONVENTIONS, END_OF_MONTH_CONVENTIONS
from scripts.common.common import to_pd_date, to_ql_date, get_day_counter

def generate_dirty_prices(bonds_df : pd.DataFrame) -> pd.DataFrame:
    """Calculate dirty prices from clean prices and accrued interest.

    Accrued interest = coupon amount × yearFraction(previous coupon, settlement)
    / yearFraction(previous coupon, next coupon), with the day count of each bond and
    settlement = evaluation date + 2 TARGET business days.

    Args:
        bonds_df: DataFrame containing the bond information and clean prices.

    Returns:
        DataFrame with the columns Bond, Maturity and DirtyPrice.
    """
    
    dirty_prices = []

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

        clean_price = row.CleanPrice

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                                CALENDAR_SCHEDULE_CONVENTIONS["OAT"], BUSINESS_DAY_CONVENTIONS["OAT"], 
                                BUSINESS_DAY_CONVENTIONS["OAT"], DATE_GENERATION_CONVENTIONS["OAT"], 
                                END_OF_MONTH_CONVENTIONS["OAT"])

        previous_coupon = None
        next_coupon = None

        for date in schedule:

            if date <= settlement:

                previous_coupon = date

            elif date > settlement:

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