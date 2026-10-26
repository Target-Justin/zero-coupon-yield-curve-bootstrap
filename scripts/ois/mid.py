import pandas as pd

def generate_mid(ois_df : pd.DataFrame) -> pd.DataFrame:
    """Calculate the mid rate of each OIS from its bid and ask quotes.

    The overnight cash rate (Freq equal to 0) is skipped: only the swaps are kept.

    Args:
        ois_df: DataFrame containing the raw OIS quotes, with the columns Ticker, Term, Unit,
                Bid and Ask (in percent), Daycount and Freq.

    Returns:
        DataFrame with the columns Ticker, Term, Unit, Mid and Daycount.
        Mid is the average of the bid and ask quotes, in decimal.
    """

    mid = []

    for row in ois_df.itertuples():

        ticker = row.Ticker
        ask = row.Ask / 100
        bid = row.Bid / 100
        freq = row.Freq

        term = row.Term
        unit = row.Unit
        day_count = row.Daycount

        if freq == 0:
            continue

        mid_rate = (ask + bid) / 2

        mid.append({"Ticker" : ticker, "Term" : term, "Unit" : unit, "Mid" : mid_rate, "Daycount" : day_count})

    return pd.DataFrame(mid)