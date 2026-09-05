import pandas as pd
import QuantLib as ql

def to_ql_date(date):
    return ql.Date(date.day, date.month, date.year)

def to_pd_date(date):
    return pd.Timestamp(date.year(), date.month(), date.dayOfMonth())

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
            f"Convention DayCount inconnue : {day_count}"
        )

def generate_dirty_prices(bonds_df : pd.DataFrame, nominal : float = 100.0) -> pd.DataFrame:
    """Calculate dirty prices from clean prices and accrued interest.

    Args:
        bonds_df: DataFrame containing bond information and clean prices.
        nominal: Nominal value of each bond.

    Returns:
        DataFrame containing the dirty price for each bond.
    """
    
    dirty_prices = []

    calendar = ql.NullCalendar()

    for row in bonds_df.itertuples():

        maturity = to_ql_date(row.Maturity)
        evaluation = to_ql_date(row.EvaluationDate)
        accrual_start_date = to_ql_date(row.AccrualStartDate)
        frequency = row.Frequency
        bond = row.Bond
        months_per_period = 12 // frequency
        coupon_amount = nominal * row.Coupon / frequency
        clean_price = row.CleanPrice

        settlement = calendar.advance(evaluation, 2, ql.Days)

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                                       calendar, ql.Unadjusted, ql.Unadjusted, ql.DateGeneration.Backward, False)

        previous_coupon = None
        next_coupon = None

        for date in schedule:

            if date < settlement:

                previous_coupon = date

            elif date > settlement:

                next_coupon = date

                break

            elif date == settlement:

                previous_coupon = date

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