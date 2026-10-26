import pandas as pd

from config import NOMINAL
from scripts.common.common import log_linear_interpolation

def ois_npv(maturity_discount_factor : float, pillar_cashflows : pd.DataFrame, discount_factors : dict, maturity : pd.Timestamp, settlement : pd.Timestamp) -> float:
    """Calculate the NPV of an OIS treated as a par bond, as a function of its maturity discount factor.

    The NPV is the present value of the cash flows minus the nominal. It is zero when
    maturity_discount_factor is the discount factor of the pillar, so the bootstrap looks for its root.
    The discount factor of each payment date comes from:
        - maturity_discount_factor, for the maturity;
        - discount_factors, for the dates already known (earlier pillars or interpolated dates);
        - a log-linear interpolation between the last pillar and the maturity, for the other dates.

    Args:
        maturity_discount_factor: Discount factor of the maturity, the unknown of the equation.
        pillar_cashflows: Cash flows of the ticker to solve.
        discount_factors: Discount factors already known, by date. Its latest date is the last pillar.
        maturity: Maturity of the ticker.
        settlement: Settlement date, origin of the time used by the interpolation.

    Returns:
        NPV of the cash flows (present value minus nominal), zero at the solution.
    """

    last_pillar = max(discount_factors)
    days_to_last_pillar = (last_pillar - settlement).days
    last_pillar_discount_factor = discount_factors[last_pillar]
    days_to_maturity = (maturity - settlement).days

    total_pv = 0.0

    for cf in pillar_cashflows.itertuples():

        amount = cf.Cashflow
        payment_date = cf.PaymentDate
        days_to_payment = (payment_date - settlement).days

        if payment_date == maturity:

            total_pv += amount * maturity_discount_factor

        elif payment_date in discount_factors:

            total_pv += amount * discount_factors[payment_date]

        else:

            total_pv += amount * log_linear_interpolation(days_to_payment, days_to_last_pillar, last_pillar_discount_factor, days_to_maturity, maturity_discount_factor)

    return total_pv - NOMINAL

def interpolated_discount_factors(maturity_discount_factor : float, missing_dates : list, discount_factors : dict, maturity : pd.Timestamp, settlement : pd.Timestamp) -> dict:
    """Calculate the discount factors of a pillar once its maturity discount factor is solved.

    The payment dates without a discount factor (missing_dates) lie between the last pillar and
    the maturity: their discount factors are interpolated log-linearly between these two points,
    with the number of calendar days since the settlement date as time.

    Args:
        maturity_discount_factor: Discount factor of the maturity, solved by the bootstrap.
        missing_dates: Payment dates of the ticker that have no discount factor yet.
        discount_factors: Discount factors already known, by date. Its latest date is the last pillar.
        maturity: Maturity of the ticker.
        settlement: Settlement date, origin of the time used by the interpolation.

    Returns:
        New discount factors by date: the maturity and the interpolated payment dates.
    """
    
    last_pillar = max(discount_factors)
    days_to_last_pillar = (last_pillar - settlement).days
    last_pillar_discount = discount_factors[last_pillar]
    days_to_maturity = (maturity - settlement).days

    interpolated_factors = {maturity: maturity_discount_factor}

    for date in missing_dates:

        interpolated_factors[date] = log_linear_interpolation((date - settlement).days, days_to_last_pillar, last_pillar_discount, days_to_maturity, maturity_discount_factor)
            
    return interpolated_factors