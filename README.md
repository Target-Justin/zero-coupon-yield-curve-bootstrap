# Zero-Coupon Yield Curve Bootstrap

## Overview

This project implements a zero-coupon yield curve bootstrap using French government bonds (OATs).
It was developed as a personal summer project to explore interest-rate modelling and better understand the construction of discount and zero-coupon curves, alongside the study of *Options, Futures, and Other Derivatives* by John Hull.

## Objectives

The main objectives of this project are to:

- understand the mechanics of yield curve bootstrapping;
- derive discount factors and zero-coupon rates from government bonds;
- implement the methodology from scratch;
- explore the impact of market conventions in bond pricing and yield curve construction;
- gain practical experience with Pandas for financial data processing and analysis;
- use QuantLib to price and bootstrap bonds, and compare its results with the from-scratch implementation.

## Methodology

### Valuation and Settlement

The instruments studied are French government bonds (OATs), which pay fixed annual coupons and repay their nominal value at maturity.
All valuations are performed as of 2026-07-29, using the clean closing prices observed on Euronext on that date.

OAT transactions on Euronext follow the European T+2 settlement convention. The settlement date is therefore defined as two business days after the valuation date, using the TARGET calendar:

```text
Settlement Date = Valuation Date + 2 TARGET business days
```

For the valuation date of 2026-07-29 (a Wednesday), the settlement date is Friday 2026-07-31.

The settlement date is the reference date for accrued coupon interest, for the future cash flows and for the time to maturity of the zero-coupon rates.

### Bootstrap Methodology

The bootstrap is performed in four main steps:

1. Calculate the future cash flows of each bond. Only the cash flows strictly after the settlement date are kept, since a coupon paid on the settlement date belongs to the seller. Each coupon is `NOMINAL × coupon rate / frequency`, and the nominal is added to the last cash flow.

2. Calculate dirty prices from the clean prices provided in the dataset. The accrued interest is the coupon amount multiplied by the fraction of the current coupon period elapsed at the settlement date, measured with the day-count convention of the bond. It is zero when the settlement date is a coupon date.

3. Bootstrap discount factors using:

   ```text
   Dirty Price = Σ Cash Flow(t) × Discount Factor(t)
   ```

4. Derive zero-coupon rates from the resulting discount factors.

The overall valuation and bootstrap process can be summarized as follows:

```text
                 Euronext Clean Price
                         │
                         ▼
                 Evaluation Date (T)
                         │
                         │ + 2 TARGET business days
                         ▼
                  Settlement Date
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
       Accrued Interest       Future Cash Flows
       up to Settlement       after Settlement
              │                     │
              └──────────┬──────────┘
                         ▼
                    Dirty Price
                         │
                         ▼
                 Sequential Bootstrap
                         │
                         ▼
                Discount Factors
                         │
                         ▼
               Zero-Coupon Rates
```

The bootstrap methodology is implemented from scratch.

At each maturity, the discount factor corresponding to the current maturity is obtained by subtracting the present value of previously bootstrapped cash flows from the dirty price and dividing by the remaining cash flow:

```text
DF(t_n) = [Dirty Price - Σ Cash Flow(t_i) × DF(t_i)] / Cash Flow(t_n)
```

Only previously bootstrapped discount factors are used. Therefore, the from-scratch bootstrap is performed sequentially without interpolation.
The bonds are sorted by successive maturity dates, from the shortest maturity to the longest.
Each bond therefore contributes to the bootstrap only after the discount factors associated with earlier maturities have been determined.
This sequential maturity structure is essential to the from-scratch bootstrap and avoids relying on future zero rates or interpolation.
The code enforces it: it raises an error if two bonds share the same maturity, or if a cash flow date does not match the maturity of a previously bootstrapped bond.

### QuantLib Benchmark

QuantLib is used for date handling (calendars, coupon schedules and day counters) and to implement an independent bootstrap benchmark.
Each bond is priced from its clean price with `FixedRateBondHelper`, using the same settlement convention as the from-scratch implementation.
The QuantLib curve is constructed using `PiecewiseLogLinearDiscount`, providing a LogLinear interpolation between bootstrapped discount factors.
This provides a useful intermediate approach between the sequential from-scratch bootstrap and a fully interpolated curve, allowing the two implementations to be compared and their differences analysed.

### Zero-Coupon Rates

Zero-coupon rates are calculated using continuous compounding in both implementations:

```text
z(T) = -ln(DF(T)) / T
```

`T` is the Actual/Actual ISDA year fraction between the settlement date and the maturity.

## Implementation

The project is organized into separate folders for data, scripts, and results:

```text
zero-coupon-yield-curve-bootstrap/
├── data/
│   ├── raw/                  # Raw input data (dataset.csv)
│   └── processed/            # Processed data
├── results/
│   └── quantlib/             # QuantLib results
├── scripts/
│   ├── quantlib/             # QuantLib scripts
│   └── utils/                # Utilities and plotting
├── config.py                 # Project parameters
├── main.py                   # Main entry point
├── README.md                 # Project documentation
└── requirements.txt          # Python dependencies
```

### Main components

- `cashflow.py`: generates the future cash flows of each bond.
- `dirty_price.py`: converts clean prices into dirty prices by calculating accrued interest.
- `bootstrap.py`: performs the sequential discount-factor bootstrap.
- `zero_rates.py`: converts discount factors into zero-coupon rates.
- `quantlib/bootstrap_quantlib.py`: builds the equivalent curve using QuantLib.
- `bootstrap_validation.py`: compares the from-scratch and QuantLib results.
- `utils/plots.py`: generates the figures described in `PLOT_CONFIG`.
- `utils/utils.py`: contains date conversion and day-count utilities.
- `config.py`: centralises parameters, conventions, paths and plotting configuration.
- `main.py`: runs the complete pipeline.

### Configuration

All conventions and settings are defined in `config.py`:

- `NOMINAL`: nominal amount of each bond (100);
- `SCHEDULE_CALENDAR`: calendar used to generate coupon dates (`ql.NullCalendar`, unadjusted dates);
- `SETTLEMENT_CALENDAR` and `SETTLEMENT_DAYS`: calendar (`ql.TARGET`) and delay (2 business days) of the settlement;
- `CURVE_DAY_COUNTER`: day counter used to convert discount factors into zero-coupon rates (Actual/Actual ISDA);
- `SHOW_PLOTS`: whether the figures flagged with `"show": True` in `PLOT_CONFIG` are displayed (the zero-coupon curve and the spread between both zero-coupon rates). All the figures are saved whatever the value;
- `PLOT_CONFIG`: path, title, axis label and series of each figure.

### Input Data

`data/raw/dataset.csv` contains one row per bond with the following columns: `Bond`, `Maturity`, `EvaluationDate`, `AccrualStartDate`, `IssueDate`, `Frequency` (coupons per year), `Coupon` (annual rate, as a decimal), `CleanPrice` and `DayCount` (`ACT/ACT`, `ACT/360`, `ACT/365` or `30/360`).

## Results

The project produces the following main outputs:

- Zero-coupon yield curve
- Discount factor curves
- Comparison between the results obtained from the bootstrap and QuantLib
- CSV files containing the intermediate and final results

The processed data in `data/processed` includes:

- `cashflow.csv`
- `dirty_price.csv`
- `discount_factor.csv`

The resulting zero-coupon rates (`zero_rate.csv`) and the comparison with QuantLib (`comparison_with_quantlib_bootstrap.csv`) are stored in `results/`, while the QuantLib zero-coupon rates (`quantlib_zero_rate.csv`) are stored in `results/quantlib/`.

### Bootstrap Comparison

The from-scratch bootstrap produces a zero-coupon curve that is very close to the QuantLib result. Across the maturities considered, the maximum difference is approximately 0.25 basis points, observed at the 2037 maturity. Outside of this point, the from-scratch implementation generally produces slightly lower zero-coupon rates than QuantLib.

#### Observed Differences

The differences are not uniform across maturities. Some local deviations can be observed at different points along the curve, while the overall difference remains small.
Both implementations use the same bond dataset and market prices. However, the precise source of the observed differences has not been investigated in detail in this project.
Different QuantLib interpolation methods were also tested, including `PiecewiseLogLinearDiscount`, `PiecewiseLogCubicDiscount`, `PiecewiseLinearZero`, and `PiecewiseCubicZero`.
The two implementations may differ in several aspects of the curve construction, but no specific cause is identified here.

#### Overall Behaviour

The differences do not increase systematically with maturity. Two points stand out from the general noise floor: 2037 (+0.25 bp, the largest deviation) and 2028 (-0.07 bp, the second largest). Outside these two points, differences remain below approximately 0.02 basis points across the remaining maturities, with the exception of a marginal excursion at 2036 (-0.02 bp).
The comparison shows that the two implementations produce very similar zero-coupon curves for the dataset considered. It therefore provides a useful consistency check for the from-scratch implementation, while acknowledging that the two curves are not numerically identical.
The precise reasons for the remaining discrepancies are left open for further investigation.

### Visualizations

![Zero-coupon curve](results/zero_coupon_curve.png)

![Discount factor plots](results/comparison_of_discountfactor.png)

![Spread between zero-coupon rates](results/spread_btw_zero_coupon_rate.png)

The other figures (QuantLib zero-coupon curve, comparison of zero-coupon rates, spread between discount factors) are saved in `results/` and `results/quantlib/`.

## Assumptions and Limitations

- Valuation date: 2026-07-29
- Settlement: 2 TARGET business days after the valuation date (2026-07-31)
- Day-count convention: Actual/Actual ISDA
- Coupon dates: unadjusted (`ql.NullCalendar`, no holiday calendar applied to coupon dates). A coupon falling on a non-business day is therefore discounted at its contractual date, not at the following business day.
- Nominal: 100
- Instruments: French government bonds (OAT)
- Maturities: OATs are sorted by increasing maturity and are treated sequentially in the bootstrap.

The bootstrap is performed sequentially, using only information available up to the current maturity.
Therefore, interpolation is not used, as it would require knowledge of a future maturity point that has not yet been bootstrapped.

To accommodate this constraint, the maturities of some OATs were slightly adjusted.
The affected maturities are 2037, 2039, 2041, and 2044.
In each case, the maturity was shifted by one month so that the bootstrap could be performed without relying on interpolation or on future zero rates.

These adjustments are simplifications made for the purpose of the bootstrap and may have a minor impact on the resulting zero-coupon curve.

## How to Run

The project was developed and tested with Python 3.14.

1. Clone the repository and install the dependencies:

   ```bash
   git clone https://github.com/Target-Justin/Zero-Coupon-Yield-Curve-Bootstrap.git
   cd Zero-Coupon-Yield-Curve-Bootstrap
   pip install -r requirements.txt
   ```

   Alternatively, you can download the repository as a ZIP file and extract it locally.

2. Run the project from the root folder of the repository:

   ```bash
   python main.py
   ```

   You can also open the repository folder in VS Code and run `main.py`. The paths in `config.py` are relative to the root folder, so the project has to be run from there.

3. To display the figures flagged with `"show": True` in `PLOT_CONFIG`, set `SHOW_PLOTS = True` in `config.py`.

## Data Sources

The dataset was collected from:

- Agence France Trésor (AFT): https://www.aft.gouv.fr/fr/encours-detaille-oat
- Euronext: https://www.euronext.com/en

## Reference

*Options, Futures, and Other Derivatives*, John Hull, 11th edition, ISBN: 978-1-292-41065-4
