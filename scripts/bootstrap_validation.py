import pandas as pd

def compare_zero_coupon(quantlib_zero_coupon_rate : pd.DataFrame, zero_coupon_rate : pd.DataFrame) -> pd.DataFrame:
    """Compare the from-scratch and QuantLib zero-coupon curves, bond by bond.

    The two DataFrames are merged on Bond and Maturity. Each difference is the
    from-scratch value minus the QuantLib value. The input DataFrames are not modified.

    Args:
        quantlib_zero_coupon_rate: QuantLib results, with the columns Bond, Maturity,
            QLDiscountFactor, QLZeroCouponRate and QLZeroCouponRatePct.
        zero_coupon_rate: From-scratch results, with the columns Bond, Maturity,
            TimeToMaturity, DiscountFactor, ZeroCouponRate and ZeroCouponRatePct.

    Returns:
        DataFrame with all the columns of both inputs plus DiscountFactor_Diff,
        ZeroCouponRate_Diff (decimal) and ZeroCouponRate_DiffBp (basis points).

    Raises:
        ValueError: If a bond of the from-scratch curve is missing from the QuantLib
            results.
    """

    quantlib_zero_coupon_rate = quantlib_zero_coupon_rate.copy()
    zero_coupon_rate = zero_coupon_rate.copy()

    quantlib_zero_coupon_rate["Maturity"] = pd.to_datetime(quantlib_zero_coupon_rate["Maturity"])
    zero_coupon_rate["Maturity"] = pd.to_datetime(zero_coupon_rate["Maturity"])

    comparison = pd.merge(quantlib_zero_coupon_rate, zero_coupon_rate, on=["Bond", "Maturity"], how="inner")

    if len(comparison) != len(zero_coupon_rate):
        raise ValueError("Some bonds of the from-scratch curve are missing from the QuantLib results.")

    comparison["DiscountFactor_Diff"] = (comparison["DiscountFactor"] - comparison["QLDiscountFactor"])
    comparison["ZeroCouponRate_Diff"] = (comparison["ZeroCouponRate"] - comparison["QLZeroCouponRate"])
    comparison["ZeroCouponRate_DiffBp"] = ((comparison["ZeroCouponRatePct"] - comparison["QLZeroCouponRatePct"])) * 100

    return comparison