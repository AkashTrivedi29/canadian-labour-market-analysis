"""
=============================================================================
Tableau Public Export — Canadian Labour Market Analysis
=============================================================================
Creates a single, wide-format "master" CSV optimized for Tableau Public.
Tableau works best with one row per observation with all dimensions present.

Dashboard Views planned in Tableau:
  Sheet 1: National Employment Rate KPI + trend line
  Sheet 2: Province map — unemployment rate (latest month)
  Sheet 3: Industry % change waterfall
  Sheet 4: Demographic comparison — youth vs. prime age
  Sheet 5: Recovery scorecard bar chart
=============================================================================
"""

import pandas as pd
import numpy as np

DATA_DIR  = "/sessions/dazzling-sweet-pascal/day1_labour_market/data"

df_prov = pd.read_csv(f"{DATA_DIR}/lfs_province.csv", parse_dates=["date"])
df_ind  = pd.read_csv(f"{DATA_DIR}/lfs_industry.csv", parse_dates=["date"])
df_dem  = pd.read_csv(f"{DATA_DIR}/lfs_demographics.csv", parse_dates=["date"])

# ── Master Province Table (Tableau-ready) ─────────────────────────────────
# Add helper columns Tableau dashboards typically need
df_prov["year"]    = df_prov["date"].dt.year
df_prov["month"]   = df_prov["date"].dt.month
df_prov["year_month"] = df_prov["date"].dt.to_period("M").astype(str)
df_prov["period"]  = df_prov["date"].apply(lambda d:
    "Pre-COVID (2019)"    if d < pd.Timestamp("2020-03-01") and d.year == 2019 else
    "Pre-COVID (2020)"    if d < pd.Timestamp("2020-03-01") else
    "COVID Shock"         if d <= pd.Timestamp("2020-06-01") else
    "Early Recovery"      if d <= pd.Timestamp("2021-06-01") else
    "Full Recovery"       if d <= pd.Timestamp("2022-06-01") else
    "Post-Recovery"
)

# Province short codes for map
prov_codes = {
    "Ontario": "ON", "Quebec": "QC", "British Columbia": "BC",
    "Alberta": "AB", "Manitoba": "MB", "Saskatchewan": "SK",
    "Nova Scotia": "NS", "New Brunswick": "NB",
    "Newfoundland": "NL", "Prince Edward Island": "PE"
}
df_prov["province_code"] = df_prov["province"].map(prov_codes)

# Pre-COVID baseline for comparison
baseline = df_prov[df_prov["date"] == "2020-02-01"][["province","employment_rate","unemployment_rate"]].copy()
baseline.columns = ["province","baseline_emp_rate","baseline_unemp_rate"]
df_prov = df_prov.merge(baseline, on="province", how="left")
df_prov["emp_rate_vs_baseline"]   = df_prov["employment_rate"]   - df_prov["baseline_emp_rate"]
df_prov["unemp_rate_vs_baseline"] = df_prov["unemployment_rate"] - df_prov["baseline_unemp_rate"]

# ── Industry Table ─────────────────────────────────────────────────────────
df_ind["year"]       = df_ind["date"].dt.year
df_ind["year_month"] = df_ind["date"].dt.to_period("M").astype(str)

# Add pre-COVID base employment for each industry
ind_base = df_ind[df_ind["date"] == "2020-02-01"][["industry","employed_thousands"]].copy()
ind_base.columns = ["industry","base_employed_thousands"]
df_ind = df_ind.merge(ind_base, on="industry", how="left")
df_ind["pct_change_vs_base"] = (
    (df_ind["employed_thousands"] - df_ind["base_employed_thousands"])
    / df_ind["base_employed_thousands"] * 100
).round(2)

# ── Demographics Table ─────────────────────────────────────────────────────
df_dem["year"]       = df_dem["date"].dt.year
df_dem["year_month"] = df_dem["date"].dt.to_period("M").astype(str)
df_dem["age_sex"]    = df_dem["sex"] + " — " + df_dem["age_group"]
df_dem["is_youth"]   = df_dem["age_group"] == "15-24"

# ── National Summary Table ─────────────────────────────────────────────────
national = (
    df_prov.groupby("date")
    .apply(lambda g: pd.Series({
        "employment_rate":    np.average(g["employment_rate"],    weights=g["population_thousands"]),
        "unemployment_rate":  np.average(g["unemployment_rate"],  weights=g["population_thousands"]),
        "participation_rate": np.average(g["participation_rate"], weights=g["population_thousands"]),
        "employed_thousands": g["employed_thousands"].sum(),
    }))
    .reset_index()
)
national["year"]       = national["date"].dt.year
national["year_month"] = national["date"].dt.to_period("M").astype(str)

# ── Save all Tableau exports ───────────────────────────────────────────────
df_prov.to_csv(f"{DATA_DIR}/tableau_province.csv", index=False)
df_ind.to_csv(f"{DATA_DIR}/tableau_industry.csv",  index=False)
df_dem.to_csv(f"{DATA_DIR}/tableau_demographics.csv", index=False)
national.to_csv(f"{DATA_DIR}/tableau_national.csv",   index=False)

print("✅ Tableau export complete")
print(f"   tableau_province.csv      — {len(df_prov)} rows, {df_prov.columns.tolist()}")
print(f"   tableau_industry.csv      — {len(df_ind)} rows")
print(f"   tableau_demographics.csv  — {len(df_dem)} rows")
print(f"   tableau_national.csv      — {len(national)} rows")

# ── Print Tableau Dashboard Blueprint ─────────────────────────────────────
print("""
╔══════════════════════════════════════════════════════════════╗
║        TABLEAU PUBLIC DASHBOARD BLUEPRINT                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  DATA SOURCE: Connect all 4 CSVs (use Relationships join)    ║
║                                                              ║
║  SHEET 1 — National KPI Cards                                ║
║  • BANs: Current Employment Rate, Unemployment Rate,         ║
║    Total Employed (thousands)                                 ║
║  • Dual-axis line: employment_rate + unemployment_rate       ║
║  • Shade COVID period: March–June 2020                       ║
║  • File: tableau_national.csv                                ║
║                                                              ║
║  SHEET 2 — Province Filled Map                               ║
║  • Drag province_code → Map                                  ║
║  • Color: unemployment_rate (latest month filter)            ║
║  • Tooltip: employment_rate, employed_thousands              ║
║  • File: tableau_province.csv                                ║
║                                                              ║
║  SHEET 3 — Industry Bar Chart (% Change)                     ║
║  • Filter: date = latest (Dec 2024)                          ║
║  • X: pct_change_vs_base  |  Y: industry                     ║
║  • Color: positive=green, negative=red                       ║
║  • File: tableau_industry.csv                                ║
║                                                              ║
║  SHEET 4 — Demographic Lines                                 ║
║  • Filter: age_group IN (15-24, 25-54)                       ║
║  • X: date  |  Y: unemployment_rate                          ║
║  • Color: age_sex (4 lines)                                  ║
║  • File: tableau_demographics.csv                            ║
║                                                              ║
║  SHEET 5 — Recovery Scorecard                                ║
║  • Filter: date = Dec 2024                                   ║
║  • X: emp_rate_vs_baseline  |  Y: province                   ║
║  • Color: diverging (above/below 0)                          ║
║  • File: tableau_province.csv                                ║
║                                                              ║
║  DASHBOARD: Arrange 5 sheets + add period filter             ║
║  PUBLISH → Tableau Public                                    ║
╚══════════════════════════════════════════════════════════════╝
""")
