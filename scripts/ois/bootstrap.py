import pandas as pd
import QuantLib as ql

from scripts.common.common import to_pd_date
from scripts.ois.pillar import find_pillars, solve_pillar

def generate_discount_factors(cashflow_df : pd.DataFrame, settlement_date : ql.Date) -> pd.DataFrame:
    """Bootstrap discount factors from OIS cash flows, pillar by pillar.

    Args:
        cashflow_df: DataFrame containing the OIS cash flows.
        settlement_date: Settlement date, origin of all the discount factors.

    Returns:
        DataFrame with the columns Ticker, Maturity and DiscountFactor, sorted by Maturity.
        Ticker is None for interpolated dates. The settlement date is not included.

    Raises:
        ValueError: Propagated from find_pillars or solve_pillar.
    """

    settlement = to_pd_date(settlement_date)
    discount_factors = {settlement : 1.0}
    pillar_tickers = {} 

    for pillar in find_pillars(cashflow_df).itertuples():

        pillar_cashflows = cashflow_df[cashflow_df["Ticker"] == pillar.Ticker]
        new_discount_factors = solve_pillar(pillar_cashflows, discount_factors, pillar.Maturity, settlement)

        discount_factors.update(new_discount_factors)
        pillar_tickers[pillar.Maturity] = pillar.Ticker

    return pd.DataFrame([{"Ticker": pillar_tickers.get(date), "Maturity": date, "DiscountFactor": discount} for date, discount in sorted(discount_factors.items()) if date != settlement])