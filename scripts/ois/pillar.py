import pandas as pd

from config import SOLVER_LOWER_BOUND, SOLVER_UPPER_BOUND, SOLVER_XTOL
from scripts.ois.pricing import ois_npv, interpolated_discount_factors
from scipy.optimize import brentq

def find_pillars(cashflow_df : pd.DataFrame) -> pd.DataFrame:
    """Find the OIS pillars, sorted by increasing maturity.

    The maturity of a ticker is its latest payment date.

    Args:
        cashflow_df: DataFrame containing the OIS cash flows.

    Returns:
        DataFrame with the columns Ticker and Maturity, sorted by Maturity.

    Raises:
        ValueError: If two OIS share the same maturity.
    """

    pillars = cashflow_df.groupby("Ticker")["PaymentDate"].max().rename("Maturity").sort_values().reset_index()

    if pillars["Maturity"].duplicated().any():
        raise ValueError("Two OIS share the same maturity: the bootstrap cannot tell them apart.")

    return pillars

def solve_pillar(pillar_cashflows : pd.DataFrame, discount_factors : dict, maturity : pd.Timestamp, settlement : pd.Timestamp) -> dict:
    """Solve the discount factor of one pillar from the pillars already bootstrapped.

    Payment dates without a known discount factor are interpolated between the last
    pillar and the maturity. They depend on the maturity discount factor, so they are
    part of the equation solved by brentq.

    Args:
        pillar_cashflows: Cash flows of the ticker to solve.
        discount_factors: Discount factors already known, by date.
        maturity: Maturity of the ticker.
        settlement: Settlement date, origin of all the discount factors.

    Returns:
        New discount factors by date: the maturity and the interpolated payment dates.

    Raises:
        ValueError: If a payment date has no discount factor before the last pillar,
                    or if the solver finds no solution (the message names the ticker).
    """
    
    ticker = pillar_cashflows["Ticker"].iloc[0]
    last_pillar = max(discount_factors)
    missing_dates = [date for date in pillar_cashflows["PaymentDate"] if date not in discount_factors and date != maturity]

    if missing_dates and min(missing_dates) <= last_pillar:
        raise ValueError(f"Ticker {pillar_cashflows['Ticker'].iloc[0]}: discount factor(s) missing at {missing_dates}, before the last bootstrapped pillar ({last_pillar}). Interpolation only applies beyond the last pillar: check that cash flow payment dates match the pillar maturities.")

    try:
        maturity_discount_factor = brentq(ois_npv, SOLVER_LOWER_BOUND, SOLVER_UPPER_BOUND, args = (pillar_cashflows, discount_factors, maturity, settlement), xtol = SOLVER_XTOL)

    except ValueError as error:
        raise ValueError(f"Ticker {ticker}: no discount factor found for the maturity {maturity.date()} between {SOLVER_LOWER_BOUND} and {SOLVER_UPPER_BOUND} ({error}). "
                         "Check the quote of this ticker (aberrant value or wrong unit) and the solver bounds in config.py.") from error

    return interpolated_discount_factors(maturity_discount_factor, missing_dates, discount_factors, maturity, settlement)