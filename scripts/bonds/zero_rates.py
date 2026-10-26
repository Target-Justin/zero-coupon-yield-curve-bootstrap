import numpy as np
import pandas as pd
import QuantLib as ql

from config import SETTLEMENT_CALENDAR_CONVENTIONS, SETTLEMENT_DAYS_CONVENTIONS, CURVE_DAY_COUNTER
from scripts.common.common import to_ql_date

def generate_zero_coupon_curve(discount_factor : pd.DataFrame, evaluation_date : pd.Timestamp) -> pd.DataFrame:
    """Calculate continuously compounded zero-coupon rates from discount factors.

    The time to maturity is measured in ACT/ACT ISDA from the settlement date
    (evaluation date + 2 TARGET business days).

    Args:
        discount_factor: DataFrame containing the bootstrapped discount factors.
        evaluation_date: Evaluation date of the market data. The settlement date derived from it is
                         the origin of the time to maturity.

    Returns:
        DataFrame with the columns Bond, Maturity, TimeToMaturity, DiscountFactor, ZeroCouponRate
        and ZeroCouponRatePct.
    """

    evaluation_date = to_ql_date(evaluation_date)

    settlement_date = SETTLEMENT_CALENDAR_CONVENTIONS["OAT"].advance(evaluation_date, SETTLEMENT_DAYS_CONVENTIONS["OAT"], ql.Days)

    time_to_maturity = discount_factor["Maturity"].apply(lambda x: CURVE_DAY_COUNTER["OAT"].yearFraction(settlement_date, to_ql_date(x)))

    zero_coupon_rate = -np.log(discount_factor["DiscountFactor"]) / time_to_maturity

    zero_coupon = pd.DataFrame({"Bond": discount_factor["Bond"],
                                    "Maturity": discount_factor["Maturity"], 
                                    "TimeToMaturity": time_to_maturity,
                                    "DiscountFactor": discount_factor["DiscountFactor"],
                                    "ZeroCouponRate": zero_coupon_rate,
                                    "ZeroCouponRatePct": zero_coupon_rate * 100})

    return zero_coupon