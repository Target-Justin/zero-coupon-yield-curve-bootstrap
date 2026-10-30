import pandas as pd
import QuantLib as ql

from config import RAW_DIR, RESULTS_DIR, CALENDAR_SCHEDULE_CONVENTIONS, SETTLEMENT_DAYS_CONVENTIONS, BUSINESS_DAY_CONVENTIONS
from scripts.common.common import to_ql_date, read_csv_robust
from scripts.ois.mid import generate_mid
from scripts.ois.cashflow import generate_cashflows
from scripts.ois.bootstrap import generate_discount_factors
from scripts.ois.zero_rates import generate_zero_coupon_curve
from scripts.ois.quantlib.quantlib_bootstrap import generate_quantlib_zero_coupon_rate
from scripts.ois.bootstrap_validation import compare_zero_coupon
from scripts.common.plots import plot

def run_ois() -> pd.DataFrame:
    """Run the OIS bootstrap on every dataset found in data/raw/ois.

    The datasets are CSV files stored in one folder per reference rate (ESTR or SOFR) and named
    after their evaluation date (YYYY-MM-DD.csv). The results of each dataset (cash flows, discount
    factors, zero-coupon rates, QuantLib benchmark, comparison and plots) are saved in
    results/ois/<reference rate>/<evaluation date>/.

    The zero-coupon curves of all datasets are also gathered in a single long-format file,
    results/ois/zero_rate.csv, with one row per (Curve, EvaluationDate, Ticker):
    Curve, EvaluationDate, SettlementDate, then the columns of generate_zero_coupon_curve
    (TimeToMaturity and DiscountFactor are measured from SettlementDate), then Bid and Ask
    (raw par swap quotes, in percent) and BidAskSpreadBp (Ask - Bid, in basis points).
    This file is the input of the Nelson-Siegel-Svensson calibration project.

    Returns:
        pd.DataFrame: The gathered zero-coupon curves (content of results/ois/zero_rate.csv).

    Raises:
        FileNotFoundError: If no dataset is found in data/raw/ois.
        ValueError: If a pillar has no bid/ask quote, or a non-positive bid-ask spread.
    """

    root = RAW_DIR["OIS"]
    files = sorted(root.glob("*/*.csv"))

    if not files:
        raise FileNotFoundError(f"No OIS dataset found in {root}. Expected one CSV file per date (YYYY-MM-DD.csv) in {root / 'ESTR'} or {root / 'SOFR'}. "
                                "The Bloomberg datasets are not published with the repository: see the Reproducibility section of the README.")

    zero_rate_list = []

    for file in files:

        ois_dataset = read_csv_robust(file, numeric_columns=("Term", "Bid", "Ask", "Freq"))
        reference_rate = file.parent.name

        output_dir = RESULTS_DIR["OIS"] / reference_rate / file.stem
        output_dir.mkdir(parents = True, exist_ok = True)

        calendar = CALENDAR_SCHEDULE_CONVENTIONS[reference_rate]

        evaluation_date = pd.to_datetime(file.stem)
        evaluation_date = to_ql_date(evaluation_date)
        settlement_date = calendar.advance(evaluation_date, SETTLEMENT_DAYS_CONVENTIONS["OIS"], ql.Days, BUSINESS_DAY_CONVENTIONS["OIS"])

        mid_df = generate_mid(ois_dataset)
        cashflow = generate_cashflows(mid_df, settlement_date, reference_rate)
        cashflow.to_csv(output_dir / "cashflow.csv", index = False)

        discount_factor = generate_discount_factors(cashflow, settlement_date)
        discount_factor.to_csv(output_dir / "discount_factor.csv", index = False)

        zero_coupon_rate = generate_zero_coupon_curve(discount_factor, settlement_date)
        zero_coupon_rate.to_csv(output_dir / "zero_rate.csv", index = False)

        tagged_zero_rate = zero_coupon_rate.copy()
        tagged_zero_rate.insert(0, "Curve", reference_rate)
        tagged_zero_rate.insert(1, "EvaluationDate", file.stem)
        tagged_zero_rate.insert(2, "SettlementDate", settlement_date.ISO())
        quotes = ois_dataset[["Ticker", "Bid", "Ask"]]
        tagged_zero_rate = tagged_zero_rate.merge(quotes, on = "Ticker", how = "left", validate = "one_to_one")
        tagged_zero_rate["BidAskSpreadBp"] = (tagged_zero_rate["Ask"] - tagged_zero_rate["Bid"]) * 100
        zero_rate_list.append(tagged_zero_rate)

        missing = tagged_zero_rate.loc[tagged_zero_rate["BidAskSpreadBp"].isna(), "Ticker"].tolist()
        if missing:
            raise ValueError(f"{reference_rate} {file.stem}: no bid/ask quote found for the tickers {missing}.")

        non_positive = tagged_zero_rate.loc[tagged_zero_rate["BidAskSpreadBp"] <= 0, "Ticker"].tolist()
        if non_positive:
            raise ValueError(f"{reference_rate} {file.stem}: non-positive bid-ask spread (Ask <= Bid) for the tickers {non_positive}.")

        quantlib_zero_coupon_rate = generate_quantlib_zero_coupon_rate(mid_df, evaluation_date, reference_rate)
        quantlib_zero_coupon_rate.to_csv(output_dir / "quantlib_zero_rate.csv", index = False)
    
        comparison = compare_zero_coupon(quantlib_zero_coupon_rate, zero_coupon_rate)
        comparison.to_csv(output_dir / "comparison_with_quantlib_bootstrap.csv", index = False)

        plot(zero_coupon_rate, "ois_zero_coupon_curve", output_dir)
        plot(quantlib_zero_coupon_rate, "ois_quantlib_zero_coupon_curve", output_dir)
        plot(comparison, "ois_comparison_discount_factor", output_dir)
        plot(comparison, "ois_comparison_zero_coupon_rate", output_dir)
        plot(comparison, "ois_spread_zero_coupon_rate", output_dir)
        plot(comparison, "ois_spread_discount_factor", output_dir)

    zero_rate_all = pd.concat(zero_rate_list, ignore_index = True)
    zero_rate_all.to_csv(RESULTS_DIR["OIS"] / "zero_rate.csv", index = False)

    return zero_rate_all