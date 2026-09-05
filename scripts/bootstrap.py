import pandas as pd

def to_pd_date(date):
    return pd.Timestamp(date.year(), date.month(), date.dayOfMonth())

def generate_discount_factors(cashflow_df : pd.DataFrame, dirty_price_df : pd.DataFrame) -> pd.DataFrame:
    """Bootstrap discount factors from bond cash flows and dirty prices.

    Args:
        cashflow_df: DataFrame containing the bond cash flows.
        dirty_price_df: DataFrame containing the dirty price of each bond.

    Returns:
        DataFrame containing the bootstrapped discount factors.
    """

    discount_factors = {}
    bonds = {}

    for bond_row in dirty_price_df.itertuples():

        bond = bond_row.Bond
        price = bond_row.DirtyPrice
        maturity = bond_row.Maturity

        known_cfXdf = 0.0
        bond_cashflows = cashflow_df[cashflow_df["Bond"] == bond]
        payment_date = bond_cashflows["Date"].iloc[-1]

        for cf in cashflow_df[cashflow_df["Bond"] == bond].itertuples():

            cashflow_amount = float(cf.Cashflow)
            date = cf.Date
            
            if date == payment_date:

               discount_factors[payment_date] = (price - known_cfXdf) / cashflow_amount
               bonds[payment_date] = bond

            elif date in discount_factors:

                known_cfXdf += discount_factors[date]*cashflow_amount

            else:

                raise ValueError("One of the discount factors needed to bootstrap is absent. This means that the dataset used doesn't have successive maturities bond.")

    return pd.DataFrame([{"Bond": bonds[date], "Maturity": date, "DiscountFactor": discount_factor} for date, discount_factor in discount_factors.items()])