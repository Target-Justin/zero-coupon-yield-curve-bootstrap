import QuantLib as ql

from pathlib import Path

RAW_DATA_PATH = Path("data/raw") / "dataset.csv"
PROCESSED_DIR = Path("data/processed")
RESULTS_DIR = {"OAT" : Path("results"), "QUANTLIB_OAT" : Path("results/quantlib"), "COMPARISON_OAT" : Path("results")}

NOMINAL = 100.0

SCHEDULE_CALENDAR = ql.NullCalendar()
SETTLEMENT_CALENDAR = ql.TARGET()
SETTLEMENT_DAYS = 2

CURVE_DAY_COUNTER = ql.ActualActual(ql.ActualActual.ISDA)

SHOW_PLOTS = False

PLOT_CONFIG = {
            "zero_coupon_curve": {"path": RESULTS_DIR["OAT"] / "zero_coupon_curve.png", 
                                    "title": "Zero coupon rate curve",
                                    "ylabel": "Zero coupon rate (%)",
                                    "figsize": (10, 6),
                                    "show": True,
                                    "series": [{"column": "ZeroCouponRatePct", "label": "Zero coupon rate (%)"}],},
            "quantlib_zero_coupon_curve": {"path": RESULTS_DIR["QUANTLIB_OAT"] / "quantlib_zero_coupon_curve.png",
                                           "title": "QL zero coupon rate curve",
                                           "ylabel": "Zero coupon rate (%)",
                                           "figsize": (10, 6),
                                           "series": [{"column": "QLZeroCouponRatePct", "label": "QuantLib zero coupon rate (%)"}],},
            "comparison_discount_factor": {"path": RESULTS_DIR["OAT"] / "comparison_of_discountfactor.png",
                                           "title": "Comparison of discount factors",
                                           "ylabel": "Discount factor",
                                           "series": [{"column": "QLDiscountFactor", "label": "QuantLib discount factor"},
                                                      {"column": "DiscountFactor", "label": "Discount factor", "marker": "x", "linestyle": "--"},],},
            "comparison_zero_coupon_rate": {"path": RESULTS_DIR["OAT"] / "zero_coupon_rate_curve.png",
                                            "title": "Comparison of zero coupon rates",
                                            "ylabel": "Zero coupon rate (%)",
                                            "series": [{"column": "QLZeroCouponRatePct", "label": "QuantLib zero coupon rate (%)"},
                                                       {"column": "ZeroCouponRatePct", "label": "Zero coupon rate (%)", "marker": "x", "linestyle": "--"},],},
            "spread_zero_coupon_rate": {"path": RESULTS_DIR["OAT"] / "spread_btw_zero_coupon_rate.png",
                                        "title": "Spread between zero coupon rates (from-scratch - QuantLib)",
                                        "ylabel": "Spread (basis points)",
                                        "figsize": (12, 5),
                                        "zero_line": True,
                                        "show": True,
                                        "series": [{"column": "ZeroCouponRate_DiffBp", "label": "Spread"}],},
            "spread_discount_factor": {"path": RESULTS_DIR["OAT"] / "spread_btw_discount_factor.png",
                                       "title": "Spread between discount factors (from scratch - QuantLib)",
                                       "ylabel": "Difference in discount factor", "figsize": (12, 5), "zero_line": True,
                                       "series": [{"column": "DiscountFactor_Diff", "label": "Spread"}],},}