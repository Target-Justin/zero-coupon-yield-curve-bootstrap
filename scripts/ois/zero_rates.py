import numpy as np
import pandas as pd
import QuantLib as ql

from config import CURVE_DAY_COUNTER
from scripts.common.common import to_ql_date

def generate_zero_coupon_curve(discount_factor : pd.DataFrame, settlement_date : ql.Date):
    """Calculate zero-coupon rates from discount factors.

    Only the pillars are kept: the interpolated dates (empty Ticker) are dropped.
    The rates are continuously compounded and the time to maturity uses the Actual/360 day count.

    Args:
        discount_factor: DataFrame containing the bootstrapped discount factors, as returned by generate_discount_factors.
        settlement_date: Settlement date, origin of the time to maturity.

    Returns:
        DataFrame with the columns Ticker, Maturity, TimeToMaturity, DiscountFactor, ZeroCouponRate
        and ZeroCouponRatePct, one row per pillar.
    """

    discount_factor = discount_factor.dropna(subset = ["Ticker"]).reset_index(drop = True)

    time_to_maturity = discount_factor["Maturity"].apply(lambda x: CURVE_DAY_COUNTER["OIS"].yearFraction(settlement_date, to_ql_date(x)))

    zero_coupon_rate = -np.log(discount_factor["DiscountFactor"]) / time_to_maturity

    zero_coupon = pd.DataFrame({"Ticker": discount_factor["Ticker"],
                                    "Maturity": discount_factor["Maturity"], 
                                    "TimeToMaturity": time_to_maturity,
                                    "DiscountFactor": discount_factor["DiscountFactor"],
                                    "ZeroCouponRate": zero_coupon_rate,
                                    "ZeroCouponRatePct": zero_coupon_rate * 100})

    return zero_coupon