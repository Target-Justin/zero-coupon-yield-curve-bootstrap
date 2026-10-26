import matplotlib.pyplot as plt
import pandas as pd

from config import PLOT_CONFIG, SHOW_PLOTS
from pathlib import Path

def plot(df: pd.DataFrame, key: str, output_dir: Path = None) -> None:
    """Draw the figure described by PLOT_CONFIG[key] against the "Maturity" column.

    The figure is saved at the path given in the config, optionally shown
    (SHOW_PLOTS), and always closed so that looping over many files does not
    accumulate open figures.

    Args:
        df: DataFrame with a "Maturity" column and the columns named in the spec.
        key: Key of the figure in PLOT_CONFIG.
        output_dir: Folder where the figure is saved, under the file name given in the config.
                    If None, the path given in the config is used.
    """
    spec = PLOT_CONFIG[key]

    if output_dir is None:
        path = spec["path"]
    else:
        path = output_dir / spec["path"].name

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
    fig.savefig(path, dpi=300, bbox_inches="tight")

    if SHOW_PLOTS and spec.get("show", False):
        plt.show()

    plt.close(fig)