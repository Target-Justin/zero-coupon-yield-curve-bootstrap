import numpy as np
import pandas as pd
import QuantLib as ql

from config import SETTLEMENT_CALENDAR, SETTLEMENT_DAYS, CURVE_DAY_COUNTER
from scripts.utils.utils import to_ql_date

def generate_zero_coupon_curve(discount_factor : pd.DataFrame, evaluation_date : pd.Timestamp) -> pd.DataFrame:
    """Calculate continuously compounded zero-coupon rates from discount factors.

    The time to maturity is measured from the settlement date (SETTLEMENT_DAYS
    business days after the evaluation date) with CURVE_DAY_COUNTER, and the rate is
    -ln(DF) / time to maturity.

    Args:
        discount_factor: DataFrame with the columns Bond, Maturity and DiscountFactor.
        evaluation_date: Valuation date of the market data.

    Returns:
        DataFrame with the columns Bond, Maturity, TimeToMaturity (in years),
        DiscountFactor, ZeroCouponRate (decimal) and ZeroCouponRatePct (percent).
    """

    evaluation_date = to_ql_date(evaluation_date)

    settlement_date = SETTLEMENT_CALENDAR.advance(evaluation_date, SETTLEMENT_DAYS, ql.Days)

    time_to_maturity = discount_factor["Maturity"].apply(lambda x: CURVE_DAY_COUNTER.yearFraction(settlement_date, to_ql_date(x)))

    zero_coupon_rate = -np.log(discount_factor["DiscountFactor"]) / time_to_maturity

    zero_coupon = pd.DataFrame({"Bond": discount_factor["Bond"],
                                    "Maturity": discount_factor["Maturity"], 
                                    "TimeToMaturity": time_to_maturity,
                                    "DiscountFactor": discount_factor["DiscountFactor"],
                                    "ZeroCouponRate": zero_coupon_rate,
                                    "ZeroCouponRatePct": zero_coupon_rate * 100})

    return zero_coupon