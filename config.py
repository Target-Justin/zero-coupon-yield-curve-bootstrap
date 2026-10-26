import QuantLib as ql

from pathlib import Path

RAW_DIR = {"OAT" : Path("data/raw/bonds") / "dataset.csv", "OIS" : Path("data/raw/ois")}
PROCESSED_DIR = {"OAT" : Path("data/processed/bonds"), "OIS" : Path("data/processed/ois")}
RESULTS_DIR = {"OAT" : Path("results/bonds"), "OIS" : Path("results/ois"), "QUANTLIB_OAT" : Path("results/bonds/quantlib"), "QUANTLIB_OIS" : Path("results/ois/quantlib"), "COMPARISON_OAT" : Path("results/bonds"), "COMPARISON_OIS" : Path("results/ois")}

NOMINAL = 100.0
TENOR_UNITS = {"DY" : ql.Days, "WK" : ql.Weeks, "MO" : ql.Months, "YR" : ql.Years}

CALENDAR_SCHEDULE_CONVENTIONS = {"OAT" : ql.NullCalendar(), "ESTR" : ql.TARGET(), "SOFR" : ql.UnitedStates(ql.UnitedStates.SOFR)}
SETTLEMENT_CALENDAR_CONVENTIONS = {"OAT" : ql.TARGET()}
SETTLEMENT_DAYS_CONVENTIONS = {"OAT" : 2, "OIS" : 2}
OVERNIGHT_INDEX_CONVENTIONS = {"ESTR" : ql.Estr(), "SOFR" : ql.Sofr()}
BUSINESS_DAY_CONVENTIONS = {"OAT" : ql.Unadjusted, "OIS" : ql.ModifiedFollowing}
DATE_GENERATION_CONVENTIONS = {"OAT" : ql.DateGeneration.Backward, "OIS" : ql.DateGeneration.Forward}
PAYMENT_PERIOD_CONVENTIONS = {"OIS" : ql.Period(ql.Annual)}
END_OF_MONTH_CONVENTIONS = {"OAT" : False, "OIS" : False}

CURVE_DAY_COUNTER = {"OAT" : ql.ActualActual(ql.ActualActual.ISDA), "OIS" : ql.Actual360()}

SOLVER_LOWER_BOUND = 1e-6
SOLVER_UPPER_BOUND = 2
SOLVER_XTOL = 1e-14

SHOW_PLOTS = True
PLOT_CONFIG = {
            "oat_zero_coupon_curve": {"path": RESULTS_DIR["OAT"] / "zero_coupon_curve.png", 
                                    "title": "Zero coupon rate curve",
                                    "ylabel": "Zero coupon rate (%)",
                                    "figsize": (10, 6),
                                    "show": True,
                                    "series": [{"column": "ZeroCouponRatePct", "label": "Zero coupon rate (%)"}],},
            "oat_quantlib_zero_coupon_curve": {"path": RESULTS_DIR["QUANTLIB_OAT"] / "quantlib_zero_coupon_curve.png",
                                           "title": "QL zero coupon rate curve",
                                           "ylabel": "Zero coupon rate (%)",
                                           "figsize": (10, 6),
                                           "series": [{"column": "QLZeroCouponRatePct", "label": "QuantLib zero coupon rate (%)"}],},
            "oat_comparison_discount_factor": {"path": RESULTS_DIR["OAT"] / "comparison_of_discountfactor.png",
                                           "title": "Comparison of discount factors",
                                           "ylabel": "Discount factor",
                                           "series": [{"column": "QLDiscountFactor", "label": "QuantLib discount factor"},
                                                      {"column": "DiscountFactor", "label": "Discount factor", "marker": "x", "linestyle": "--"},],},
            "oat_comparison_zero_coupon_rate": {"path": RESULTS_DIR["OAT"] / "zero_coupon_rate_curve.png",
                                            "title": "Comparison of zero coupon rates",
                                            "ylabel": "Zero coupon rate (%)",
                                            "series": [{"column": "QLZeroCouponRatePct", "label": "QuantLib zero coupon rate (%)"},
                                                       {"column": "ZeroCouponRatePct", "label": "Zero coupon rate (%)", "marker": "x", "linestyle": "--"},],},
            "oat_spread_zero_coupon_rate": {"path": RESULTS_DIR["OAT"] / "spread_btw_zero_coupon_rate.png",
                                        "title": "Spread between zero coupon rates (from-scratch - QuantLib)",
                                        "ylabel": "Spread (basis points)",
                                        "figsize": (12, 5),
                                        "zero_line": True,
                                        "show": True,
                                        "series": [{"column": "ZeroCouponRate_DiffBp", "label": "Spread"}],},
            "oat_spread_discount_factor": {"path": RESULTS_DIR["OAT"] / "spread_btw_discount_factor.png",
                                       "title": "Spread between discount factors (from scratch - QuantLib)",
                                       "ylabel": "Difference in discount factor", "figsize": (12, 5), "zero_line": True,
                                       "series": [{"column": "DiscountFactor_Diff", "label": "Spread"}],},
            "ois_zero_coupon_curve": {"path": RESULTS_DIR["OIS"] / "zero_coupon_curve.png",
                                      "title": "OIS zero coupon rate curve",
                                      "ylabel": "Zero coupon rate (%)",
                                      "figsize": (10, 6),
                                      "series": [{"column": "ZeroCouponRatePct", "label": "Zero coupon rate (%)"}],},
            "ois_quantlib_zero_coupon_curve": {"path": RESULTS_DIR["QUANTLIB_OIS"] / "quantlib_zero_coupon_curve.png",
                                               "title": "OIS QL zero coupon rate curve",
                                               "ylabel": "Zero coupon rate (%)",
                                               "figsize": (10, 6),
                                               "series": [{"column": "QLZeroCouponRatePct", "label": "QuantLib zero coupon rate (%)"}],},
            "ois_comparison_discount_factor": {"path": RESULTS_DIR["COMPARISON_OIS"] / "comparison_of_discountfactor.png",
                                               "title": "OIS comparison of discount factors",
                                               "ylabel": "Discount factor",
                                               "series": [{"column": "QLDiscountFactor", "label": "QuantLib discount factor"},
                                                          {"column": "DiscountFactor", "label": "Discount factor", "marker": "x", "linestyle": "--"},],},
            "ois_comparison_zero_coupon_rate": {"path": RESULTS_DIR["COMPARISON_OIS"] / "zero_coupon_rate_curve.png",
                                                "title": "OIS comparison of zero coupon rates",
                                                "ylabel": "Zero coupon rate (%)",
                                                "series": [{"column": "QLZeroCouponRatePct", "label": "QuantLib zero coupon rate (%)"},
                                                           {"column": "ZeroCouponRatePct", "label": "Zero coupon rate (%)", "marker": "x", "linestyle": "--"},],},
            "ois_spread_zero_coupon_rate": {"path": RESULTS_DIR["COMPARISON_OIS"] / "spread_btw_zero_coupon_rate.png",
                                            "title": "OIS spread between zero coupon rates (from-scratch - QuantLib)",
                                            "ylabel": "Spread (basis points)",
                                            "figsize": (12, 5),
                                            "zero_line": True,
                                            "series": [{"column": "ZeroCouponRate_DiffBp", "label": "Spread"}],},
            "ois_spread_discount_factor": {"path": RESULTS_DIR["COMPARISON_OIS"] / "spread_btw_discount_factor.png",
                                           "title": "OIS spread between discount factors (from scratch - QuantLib)",
                                           "ylabel": "Difference in discount factor", "figsize": (12, 5), "zero_line": True,
                                           "series": [{"column": "DiscountFactor_Diff", "label": "Spread"}],},}