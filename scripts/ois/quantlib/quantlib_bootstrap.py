import pandas as pd
import QuantLib as ql

from config import TENOR_UNITS, CALENDAR_SCHEDULE_CONVENTIONS, SETTLEMENT_DAYS_CONVENTIONS, OVERNIGHT_INDEX_CONVENTIONS, CURVE_DAY_COUNTER, DATE_GENERATION_CONVENTIONS
from scripts.common.common import to_pd_date

def generate_quantlib_zero_coupon_rate(mid_df : pd.DataFrame, evaluation_date : ql.Date, reference_rate : str) -> pd.DataFrame:
    """Generate a zero-coupon curve using QuantLib.

    This curve is used as a benchmark for the from-scratch bootstrap. Each OIS becomes an
    OISRateHelper on its mid rate, and the curve is a PiecewiseLogLinearDiscount in ACT/360.
    The rates are continuously compounded.

    Side effect: sets the global QuantLib evaluation date (ql.Settings) to evaluation_date.

    Args:
        mid_df: DataFrame containing the OIS mid rates (decimal), as returned by generate_mid.
        evaluation_date: Evaluation date of the market data, set as the QuantLib evaluation date.
        reference_rate: Reference rate of the OIS (ESTR or SOFR).

    Returns:
        DataFrame with the columns Ticker, Maturity, QLDiscountFactor, QLZeroCouponRate and
        QLZeroCouponRatePct, one row per OIS.

    Raises:
        ValueError: If a day count other than ACT/360 is found, because OISRateHelper uses the day count of the index.
    """
    ql.Settings.instance().evaluationDate = evaluation_date

    calendar = CALENDAR_SCHEDULE_CONVENTIONS[reference_rate]
    index = OVERNIGHT_INDEX_CONVENTIONS[reference_rate]
    settlement_days = SETTLEMENT_DAYS_CONVENTIONS["OIS"]

    helpers = []

    for row in mid_df.itertuples():

        if row.Daycount != "ACT/360":

            raise ValueError(f"Ticker {row.Ticker}: OISRateHelper takes the day count of the index (ACT/360), not {row.Daycount}.")

        tenor = ql.Period(int(row.Term), TENOR_UNITS[row.Unit])

        quote = ql.QuoteHandle(ql.SimpleQuote(row.Mid))

        helper = ql.OISRateHelper(settlementDays = settlement_days, tenor = tenor, rate = quote, index = index,
                                  paymentCalendar = calendar, fixedCalendar = calendar, overnightCalendar = calendar,
                                  rule = DATE_GENERATION_CONVENTIONS["OIS"])

        helpers.append(helper)

    curve = ql.PiecewiseLogLinearDiscount(settlement_days, calendar, helpers, CURVE_DAY_COUNTER["OIS"])

    rows = []

    for row, helper in zip(mid_df.itertuples(), helpers):

        ticker = row.Ticker
        maturity = helper.maturityDate()

        zero_rate = curve.zeroRate(maturity, CURVE_DAY_COUNTER["OIS"], ql.Continuous).rate()

        discount_factor = curve.discount(maturity)

        rows.append({"Ticker": ticker,
                    "Maturity": to_pd_date(maturity),
                    "QLDiscountFactor": discount_factor,
                    "QLZeroCouponRate": zero_rate,
                    "QLZeroCouponRatePct": zero_rate * 100,})

    zero_coupon_rate = pd.DataFrame(rows)

    return zero_coupon_rate