import pandas as pd

def compare_zero_coupon(quantlib_zero_coupon_rate : pd.DataFrame, zero_coupon_rate : pd.DataFrame) -> pd.DataFrame:
    """Compare the from-scratch and QuantLib zero-coupon curves.

    The two curves are joined on Ticker and Maturity (inner join, one row per OIS on each side),
    so the interpolated dates of the from-scratch bootstrap are left out.

    Args:
        quantlib_zero_coupon_rate: DataFrame containing the QuantLib results.
        zero_coupon_rate: DataFrame containing the from-scratch bootstrap results.

    Returns:
        DataFrame with the columns of both inputs plus DiscountFactor_Diff, ZeroCouponRate_Diff
        (decimal) and ZeroCouponRate_DiffBp (basis points), all from-scratch minus QuantLib.
    """

    quantlib_zero_coupon_rate = quantlib_zero_coupon_rate.copy()
    zero_coupon_rate = zero_coupon_rate.copy()

    quantlib_zero_coupon_rate["Maturity"] = pd.to_datetime(quantlib_zero_coupon_rate["Maturity"])
    zero_coupon_rate["Maturity"] = pd.to_datetime(zero_coupon_rate["Maturity"])

    comparison = pd.merge(quantlib_zero_coupon_rate, zero_coupon_rate, on=["Ticker", "Maturity"], how="inner", validate="one_to_one")

    comparison["DiscountFactor_Diff"] = (comparison["DiscountFactor"] - comparison["QLDiscountFactor"])
    comparison["ZeroCouponRate_Diff"] = (comparison["ZeroCouponRate"] - comparison["QLZeroCouponRate"])
    comparison["ZeroCouponRate_DiffBp"] = ((comparison["ZeroCouponRatePct"] - comparison["QLZeroCouponRatePct"])) * 100

    return comparison