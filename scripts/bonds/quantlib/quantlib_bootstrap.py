import pandas as pd
import QuantLib as ql

from config import NOMINAL, SETTLEMENT_CALENDAR_CONVENTIONS, SETTLEMENT_DAYS_CONVENTIONS, CURVE_DAY_COUNTER, DATE_GENERATION_CONVENTIONS, BUSINESS_DAY_CONVENTIONS, END_OF_MONTH_CONVENTIONS
from scripts.common.common import to_ql_date, get_day_counter

def generate_quantlib_zero_coupon_rate(bonds_df : pd.DataFrame) -> pd.DataFrame:
    """Generate a zero-coupon curve using QuantLib.

    This curve is used as a benchmark for the from-scratch bootstrap. Each bond becomes a
    FixedRateBondHelper on its clean price, and the curve is a PiecewiseLogLinearDiscount
    in ACT/ACT ISDA. The rates are continuously compounded.

    Side effect: sets the global QuantLib evaluation date (ql.Settings) to the evaluation date
    of the data.

    Args:
        bonds_df: DataFrame containing the bond market data.

    Returns:
        DataFrame with the columns Bond, Maturity, QLDiscountFactor, QLZeroCouponRate and
        QLZeroCouponRatePct, one row per bond.
    """

    evaluation_date = to_ql_date(bonds_df["EvaluationDate"].iloc[0])
    ql.Settings.instance().evaluationDate = evaluation_date

    helpers = []

    for row in bonds_df.itertuples():

        coupon_day_counter=get_day_counter(row.DayCount)

        maturity = to_ql_date(row.Maturity)
        accrual_start_date = to_ql_date(row.AccrualStartDate)
        issue_date = to_ql_date(row.IssueDate)

        frequency = row.Frequency
        months_per_period = 12 // frequency

        coupon = row.Coupon
        clean_price = row.CleanPrice

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                            SETTLEMENT_CALENDAR_CONVENTIONS["OAT"], BUSINESS_DAY_CONVENTIONS["OAT"], BUSINESS_DAY_CONVENTIONS["OAT"],
                            DATE_GENERATION_CONVENTIONS["OAT"], END_OF_MONTH_CONVENTIONS["OAT"])

        quote = ql.QuoteHandle(ql.SimpleQuote(clean_price))

        helper = ql.FixedRateBondHelper(quote, SETTLEMENT_DAYS_CONVENTIONS["OAT"], NOMINAL, schedule,
                                        [coupon], coupon_day_counter, BUSINESS_DAY_CONVENTIONS["OAT"], NOMINAL, issue_date)

        helpers.append(helper)

    curve = ql.PiecewiseLogLinearDiscount(SETTLEMENT_DAYS_CONVENTIONS["OAT"], SETTLEMENT_CALENDAR_CONVENTIONS["OAT"], helpers, 
                                            CURVE_DAY_COUNTER["OAT"])

    rows = []

    for row in bonds_df.itertuples():

        bond = row.Bond
        maturity = row.Maturity

        zero_rate = curve.zeroRate(to_ql_date(maturity), CURVE_DAY_COUNTER["OAT"], ql.Continuous).rate()

        discount_factor = curve.discount(to_ql_date(maturity))

        rows.append({"Bond": bond, 
                    "Maturity": maturity,
                    "QLDiscountFactor": discount_factor,
                    "QLZeroCouponRate": zero_rate, 
                    "QLZeroCouponRatePct": zero_rate * 100,})

    zero_coupon_rate = pd.DataFrame(rows)

    return zero_coupon_rate