import pandas as pd

def generate_discount_factors(cashflow_df : pd.DataFrame, dirty_price_df : pd.DataFrame) -> pd.DataFrame:
    """Bootstrap discount factors sequentially from bond cash flows and dirty prices.

    Bonds are processed by increasing maturity. Every payment date before a bond's maturity
    must already have a discount factor, and the maturity one is then
    DF(t_n) = (dirty price - Σ CF(t_i) · DF(t_i)) / CF(t_n). No interpolation is used.

    Args:
        cashflow_df: Bond cash flows, as returned by generate_cashflows.
        dirty_price_df: Dirty price of each bond, as returned by generate_dirty_prices.

    Returns:
        DataFrame with the columns Bond, Maturity and DiscountFactor, one row per bond.

    Raises:
        ValueError: If two bonds share a maturity, or if a payment date has no discount factor
                    yet (the maturities are not successive).
    """

    discount_factors = {}
    bonds = {}

    dirty_price_df = dirty_price_df.sort_values("Maturity").reset_index(drop=True)

    if dirty_price_df["Maturity"].duplicated().any():
        raise ValueError("Two bonds share the same maturity: the bootstrap cannot tell them apart.")

    for bond_row in dirty_price_df.itertuples():

        bond = bond_row.Bond
        price = bond_row.DirtyPrice

        pv_known_cashflows = 0.0
        bond_cashflows = cashflow_df[cashflow_df["Bond"] == bond]
        payment_date = bond_cashflows["Date"].iloc[-1]

        for cf in bond_cashflows.itertuples():

            cashflow_amount = cf.Cashflow
            date = cf.Date
            
            if date == payment_date:

               discount_factors[payment_date] = (price - pv_known_cashflows) / cashflow_amount
               bonds[payment_date] = bond

            elif date in discount_factors:

                pv_known_cashflows += discount_factors[date] * cashflow_amount

            else:

                raise ValueError("One of the discount factors needed to bootstrap is absent. This means that the dataset used doesn't have successive maturities bond.")

    return pd.DataFrame([{"Bond": bonds[date], "Maturity": date, "DiscountFactor": discount_factor} for date, discount_factor in discount_factors.items()])