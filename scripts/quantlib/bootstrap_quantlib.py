import QuantLib as ql
import pandas as pd
import matplotlib.pyplot as plt

def to_ql_date(date):
    return ql.Date(date.day, date.month, date.year)

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

def generate_quantlib_zero_coupon_curve(bonds_df : pd.DataFrame) -> pd.DataFrame:
    """Generate a zero-coupon curve using QuantLib.

    This curve is used as a benchmark for the from-scratch bootstrap.

    Args:
        bonds_df: DataFrame containing the bond market data.

    Returns:
        DataFrame containing QuantLib discount factors and zero-coupon rates.
    """

    calendar = ql.NullCalendar()

    evaluation_date = to_ql_date(bonds_df["EvaluationDate"].iloc[0])
    ql.Settings.instance().evaluationDate = evaluation_date

    settlement_day = 2

    helpers = []

    for row in bonds_df.itertuples():

        day_counter=get_day_counter(row.DayCount)

        maturity = to_ql_date(row.Maturity)
        evaluation_date = to_ql_date(row.EvaluationDate)
        accrual_start_date = to_ql_date(row.AccrualStartDate)
        issue_date = to_ql_date(row.IssueDate)
        frequency = row.Frequency
        months_per_period = 12 // frequency
        coupon = float(row.Coupon)
        clean_price = float(row.CleanPrice)

        schedule = ql.Schedule(accrual_start_date, maturity, ql.Period(months_per_period, ql.Months),
                            calendar, ql.Unadjusted, ql.Unadjusted,
                            ql.DateGeneration.Backward,False)

        quote = ql.QuoteHandle(ql.SimpleQuote(clean_price))

        helper = ql.FixedRateBondHelper(quote, settlement_day, 100.0, schedule,
                                        [coupon], day_counter, ql.Unadjusted, 100.0,
                                        issue_date)

        helpers.append(helper)

    curve = ql.PiecewiseLogLinearDiscount(settlement_day, calendar, helpers, 
                                            day_counter)

    rows = []

    for row in bonds_df.itertuples():

        bond = row.Bond
        maturity = row.Maturity

        zero_rate = curve.zeroRate(to_ql_date(maturity), day_counter, ql.Continuous).rate()

        discount_factor = curve.discount(to_ql_date(maturity))

        rows.append({"Bond": bond, 
                    "Maturity": maturity,
                    "QLDiscountFactor": discount_factor,
                    "QLZeroCouponRate": zero_rate, 
                    "QLZeroCouponRatePct": zero_rate * 100,})

    zero_coupon = pd.DataFrame(rows)

    plt.figure(figsize=(10, 6))

    plt.plot(
        zero_coupon["Maturity"],
        zero_coupon["QLZeroCouponRatePct"],
        marker="o",
        linewidth=1.5
    )

    plt.xlabel("Maturity")
    plt.ylabel("Zero coupon rate (%)")
    plt.title("QL zero coupon rate curve")

    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig("results/quantlib/quantlib_zero_coupon_curve.png", dpi=300, bbox_inches="tight")

    plt.show()

    return zero_coupon