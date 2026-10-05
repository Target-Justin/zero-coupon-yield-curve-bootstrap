import matplotlib.pyplot as plt
import pandas as pd

from config import PLOT_CONFIG, SHOW_PLOTS

def plot(df: pd.DataFrame, key: str) -> None:
    """Draw the figure described by PLOT_CONFIG[key] against the "Maturity" column.

    The figure is always saved at the path given in the config. It is displayed only
    if SHOW_PLOTS is True and the entry of the figure has "show": True. It is always
    closed afterwards so that figures do not accumulate in memory.

    Args:
        df: DataFrame with a "Maturity" column and the columns named in the series
            of the config entry.
        key: Key of the figure in PLOT_CONFIG.
    """
    
    spec = PLOT_CONFIG[key]

    fig, ax = plt.subplots(figsize=spec.get("figsize", (12, 6)))

    if spec.get("zero_line", False):
        ax.axhline(y=0, linestyle="--", linewidth=1)

    for series in spec["series"]:
        ax.plot(df["Maturity"],
                df[series["column"]],
                marker=series.get("marker", "o"),
                linestyle=series.get("linestyle", "-"),
                label=series["label"],)

    ax.set_title(spec["title"])
    ax.set_xlabel("Maturity")
    ax.set_ylabel(spec["ylabel"])
    ax.grid(True, alpha=0.3)

    if len(spec["series"]) > 1:
        ax.legend()

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(spec["path"], dpi=300, bbox_inches="tight")

    if SHOW_PLOTS and spec.get("show", False):
        plt.show()

    plt.close(fig)