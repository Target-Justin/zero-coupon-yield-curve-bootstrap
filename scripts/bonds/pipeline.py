import pandas as pd

from config import RAW_DIR, PROCESSED_DIR, RESULTS_DIR
from scripts.bonds.cashflow import generate_cashflows
from scripts.bonds.dirty_price import generate_dirty_prices
from scripts.bonds.bootstrap import generate_discount_factors
from scripts.bonds.zero_rates import generate_zero_coupon_curve
from scripts.bonds.quantlib.quantlib_bootstrap import generate_quantlib_zero_coupon_rate
from scripts.bonds.bootstrap_validation import compare_zero_coupon
from scripts.common.plots import plot
from scripts.common.common import read_csv_robust, parse_dates

def run_bonds():
    """Run the OAT bootstrap on the dataset data/raw/bonds/dataset.csv.

    The intermediate files (cash flows, dirty prices, discount factors) are saved in data/processed/bonds
    and the results (zero-coupon rates, QuantLib benchmark, comparison and plots) in results/bonds.
    """
    
    bonds_df = read_csv_robust(RAW_DIR["OAT"], numeric_columns=("Coupon", "CleanPrice", "Frequency"))

    for folder in (PROCESSED_DIR["OAT"], RESULTS_DIR["OAT"], RESULTS_DIR["QUANTLIB_OAT"], RESULTS_DIR["COMPARISON_OAT"]):
        folder.mkdir(parents = True, exist_ok = True)

    bonds_df["Maturity"] = parse_dates(bonds_df["Maturity"])
    bonds_df["EvaluationDate"] = parse_dates(bonds_df["EvaluationDate"])
    bonds_df["AccrualStartDate"] = parse_dates(bonds_df["AccrualStartDate"])
    bonds_df["IssueDate"] = parse_dates(bonds_df["IssueDate"])

    cashflow = generate_cashflows(bonds_df)
    cashflow.to_csv(PROCESSED_DIR["OAT"] / "cashflow.csv", index = False)

    dirty_price = generate_dirty_prices(bonds_df)
    dirty_price.to_csv(PROCESSED_DIR["OAT"] / "dirty_price.csv", index = False)

    discount_factor = generate_discount_factors(cashflow, dirty_price)
    discount_factor.to_csv(PROCESSED_DIR["OAT"] / "discount_factor.csv", index = False)

    zero_coupon_rate = generate_zero_coupon_curve(discount_factor, bonds_df.loc[0, "EvaluationDate"])
    zero_coupon_rate.to_csv(RESULTS_DIR["OAT"] / "zero_rate.csv", index = False)

    quantlib_zero_coupon_rate = generate_quantlib_zero_coupon_rate(bonds_df)
    quantlib_zero_coupon_rate.to_csv(RESULTS_DIR["QUANTLIB_OAT"] / "quantlib_zero_rate.csv", index = False)

    comparison = compare_zero_coupon(quantlib_zero_coupon_rate, zero_coupon_rate)
    comparison.to_csv(RESULTS_DIR["COMPARISON_OAT"] / "comparison_with_quantlib_bootstrap.csv", index = False)

    plot(zero_coupon_rate, "oat_zero_coupon_curve")
    plot(quantlib_zero_coupon_rate, "oat_quantlib_zero_coupon_curve")
    plot(comparison, "oat_comparison_discount_factor")
    plot(comparison, "oat_comparison_zero_coupon_rate")
    plot(comparison, "oat_spread_zero_coupon_rate")
    plot(comparison, "oat_spread_discount_factor")