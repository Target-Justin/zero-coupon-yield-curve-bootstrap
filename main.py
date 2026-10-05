import pandas as pd

from config import RAW_DATA_PATH, PROCESSED_DIR, RESULTS_DIR
from scripts.cashflow import generate_cashflows
from scripts.dirty_price import generate_dirty_prices
from scripts.bootstrap import generate_discount_factors
from scripts.zero_rates import generate_zero_coupon_curve
from scripts.quantlib.bootstrap_quantlib import generate_quantlib_zero_coupon_rate
from scripts.bootstrap_validation import compare_zero_coupon
from scripts.utils.plots import plot

        
bonds_df = pd.read_csv(RAW_DATA_PATH, parse_dates = ["Maturity", "EvaluationDate", "AccrualStartDate", "IssueDate"])

cashflow = generate_cashflows(bonds_df)
cashflow.to_csv(PROCESSED_DIR / "cashflow.csv", index = False)

dirty_price = generate_dirty_prices(bonds_df)
dirty_price.to_csv(PROCESSED_DIR / "dirty_price.csv", index = False)

discount_factor = generate_discount_factors(cashflow, dirty_price)
discount_factor.to_csv(PROCESSED_DIR / "discount_factor.csv", index = False)

zero_coupon_rate = generate_zero_coupon_curve(discount_factor, bonds_df["EvaluationDate"].loc[0])
zero_coupon_rate.to_csv(RESULTS_DIR["OAT"] / "zero_rate.csv", index = False)

quantlib_zero_coupon_rate = generate_quantlib_zero_coupon_rate(bonds_df)
quantlib_zero_coupon_rate.to_csv(RESULTS_DIR["QUANTLIB_OAT"] / "quantlib_zero_rate.csv", index = False)

comparison = compare_zero_coupon(quantlib_zero_coupon_rate, zero_coupon_rate)
comparison.to_csv(RESULTS_DIR["COMPARISON_OAT"] / "comparison_with_quantlib_bootstrap.csv", index = False)

plot(zero_coupon_rate, "zero_coupon_curve")
plot(quantlib_zero_coupon_rate, "quantlib_zero_coupon_curve")
plot(comparison, "comparison_discount_factor")
plot(comparison, "comparison_zero_coupon_rate")
plot(comparison, "spread_zero_coupon_rate")
plot(comparison, "spread_discount_factor")