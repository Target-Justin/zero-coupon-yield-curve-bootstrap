import pandas as pd

def generate_discount_factors(cashflow_df : pd.DataFrame, dirty_price_df : pd.DataFrame) -> pd.DataFrame:
    """Bootstrap discount factors from bond cashflows and dirty prices.

    Bonds are processed by increasing maturity. For each bond, the discount factor
    at its maturity is (dirty price - present value of its earlier cashflows) /
    final cashflow. Every earlier cashflow date must therefore already be the
    maturity of a previous bond: no interpolation is used.

    Args:
        cashflow_df: DataFrame with the columns Bond, Date and Cashflow, one row per
            future cashflow, ordered by date within each bond.
        dirty_price_df: DataFrame with one row per bond and the columns Bond,
            Maturity and DirtyPrice.

    Returns:
        DataFrame with the columns Bond, Maturity and DiscountFactor, sorted by
        increasing maturity.

    Raises:
        ValueError: If two bonds share the same maturity, or if a cashflow date
            has no known discount factor.
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
        maturity_date = bond_cashflows["Date"].iloc[-1]

        for cf in bond_cashflows.itertuples():

            cashflow_amount = cf.Cashflow
            date = cf.Date
            
            if date == maturity_date:

               discount_factors[maturity_date] = (price - pv_known_cashflows) / cashflow_amount
               bonds[maturity_date] = bond

            elif date in discount_factors:

                pv_known_cashflows += discount_factors[date]*cashflow_amount

            else:

                raise ValueError(f"Cannot bootstrap {bond}: its cash flow on {date:%Y-%m-%d} has no known "
                 f"discount factor because no bond matures on that date. "
                 f"The dataset needs bonds with successive maturities.")
                
    return pd.DataFrame([{"Bond": bonds[date], "Maturity": date, "DiscountFactor": discount_factor} for date, discount_factor in discount_factors.items()])