import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import QuantLib as ql

def to_ql_date(date):
    return ql.Date(date.day, date.month, date.year)

def generate_zero_coupon_curve(discount_factor : pd.DataFrame, valuation_date : pd.Timestamp, compounding : str = "continuous"):
    """Calculate zero-coupon rates from discount factors.

    Args:
        discount_factor_df: DataFrame containing the bootstrapped discount factors.
        valuation_date: Valuation date used to calculate time to maturity.
        compounding: Compounding convention used to calculate zero rates.

    Returns:
        DataFrame containing maturities, discount factors, and zero-coupon rates.
    """

    calendar = ql.NullCalendar()

    valuation_date = to_ql_date(valuation_date)

    settlement_date = calendar.advance(valuation_date, 2, ql.Days)

    day_counter = ql.ActualActual(ql.ActualActual.ISDA)

    time_to_maturity = discount_factor["Maturity"].apply(lambda x: day_counter.yearFraction(settlement_date, to_ql_date(x)))

    if compounding == "continuous":

        zero_coupon_rate = -np.log(discount_factor["DiscountFactor"]) / time_to_maturity

        zero_coupon = pd.DataFrame({"Bond": discount_factor["Bond"],
                                    "Maturity": discount_factor["Maturity"], 
                                    "TimeToMaturity": time_to_maturity,
                                    "DiscountFactor": discount_factor["DiscountFactor"],
                                    "ZeroCouponRate": zero_coupon_rate,
                                    "ZeroCouponRatePct": zero_coupon_rate * 100})

    elif compounding == "annual":

        zero_coupon_rate = discount_factor["DiscountFactor"] ** (-1.0 / time_to_maturity) - 1.0

        zero_coupon = pd.DataFrame({"Bond": discount_factor["Bond"],
                                    "Maturity": discount_factor["Maturity"], 
                                    "TimeToMaturity": time_to_maturity,
                                    "DiscountFactor": discount_factor["DiscountFactor"],
                                    "ZeroCouponRate": zero_coupon_rate,
                                    "ZeroCouponRatePct": zero_coupon_rate * 100})

    else:
        
        raise ValueError(f"Compounding inconnu : {compounding}")

    plt.figure(figsize=(10, 6))

    plt.plot(
        zero_coupon["Maturity"],
        zero_coupon["ZeroCouponRatePct"],
        marker="o"
    )

    plt.xlabel("Maturity")
    plt.ylabel("Zero coupon rate (%)")
    plt.title("Zero coupon rate curve")
    plt.grid(True)

    plt.tight_layout()

    plt.savefig("results/zero_coupon_curve.png", dpi=300, bbox_inches="tight")

    plt.show()

    return zero_coupon