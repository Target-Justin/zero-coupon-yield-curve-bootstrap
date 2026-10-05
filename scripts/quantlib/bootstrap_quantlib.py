import pandas as pd
import QuantLib as ql

from config import NOMINAL, SETTLEMENT_CALENDAR, SETTLEMENT_DAYS, CURVE_DAY_COUNTER
from scripts.utils.utils import to_ql_date, get_day_counter

def generate_quantlib_zero_coupon_rate(bonds_df : pd.DataFrame) -> pd.DataFrame:
    """Bootstrap a zero-coupon curve with QuantLib, used as a benchmark.

    One FixedRateBondHelper is built per bond from its clean price, then a
    PiecewiseLogLinearDiscount curve is bootstrapped. The curve starts at the
    settlement date, SETTLEMENT_DAYS business days after the evaluation date of the
    first row, which is also set as the global QuantLib evaluation date. Discount
    factors and continuously compounded zero rates (CURVE_DAY_COUNTER) are read at
    the maturity of each bond.

    Args:
        bonds_df: DataFrame with one row per bond and the columns Bond, Maturity,
            EvaluationDate, AccrualStartDate, IssueDate, Frequency (coupons per
            year), Coupon (annual rate as a decimal), CleanPrice and DayCount.

    Returns:
        DataFrame with the columns Bond, Maturity, QLDiscountFactor,
        QLZeroCouponRate (decimal) and QLZeroCouponRatePct (percent).
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
                            SETTLEMENT_CALENDAR, ql.Unadjusted, ql.Unadjusted,
                            ql.DateGeneration.Backward,False)

        quote = ql.QuoteHandle(ql.SimpleQuote(clean_price))

        helper = ql.FixedRateBondHelper(quote, SETTLEMENT_DAYS, NOMINAL, schedule,
                                        [coupon], coupon_day_counter, ql.Unadjusted, NOMINAL, issue_date)

        helpers.append(helper)

    curve = ql.PiecewiseLogLinearDiscount(SETTLEMENT_DAYS, SETTLEMENT_CALENDAR, helpers, 
                                            CURVE_DAY_COUNTER)

    rows = []

    for row in bonds_df.itertuples():

        bond = row.Bond
        maturity = row.Maturity

        zero_rate = curve.zeroRate(to_ql_date(maturity), CURVE_DAY_COUNTER, ql.Continuous).rate()

        discount_factor = curve.discount(to_ql_date(maturity))

        rows.append({"Bond": bond, 
                    "Maturity": maturity,
                    "QLDiscountFactor": discount_factor,
                    "QLZeroCouponRate": zero_rate, 
                    "QLZeroCouponRatePct": zero_rate * 100,})

    zero_coupon_rate = pd.DataFrame(rows)

    return zero_coupon_rate