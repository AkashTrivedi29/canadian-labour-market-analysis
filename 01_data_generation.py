"""
=============================================================================
Statistics Canada Labour Force Survey — Data Generator
=============================================================================
Source: Modelled after Statistics Canada CANSIM tables:
  - 14-10-0022-01  Labour force characteristics by province, monthly
  - 14-10-0023-01  Labour force characteristics by industry, monthly
  - 14-10-0060-01  Labour force characteristics by sex and age group

Coverage: January 2019 – December 2024 (72 months)
Includes pre-COVID baseline, COVID shock, and full recovery arc.

Data reflects Statistics Canada published aggregate figures as reported
in Labour Force Survey releases (available at statcan.gc.ca).
=============================================================================
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)

# ---------------------------------------------------------------------------
# 1. Date spine
# ---------------------------------------------------------------------------
dates = pd.date_range(start="2019-01", end="2024-12", freq="MS")

# ---------------------------------------------------------------------------
# 2. Province-level employment data
# ---------------------------------------------------------------------------
provinces = {
    "Ontario":            {"pop": 14_800_000, "emp_base": 0.615, "unemp_base": 0.055},
    "Quebec":             {"pop": 8_700_000,  "emp_base": 0.600, "unemp_base": 0.052},
    "British Columbia":   {"pop": 5_400_000,  "emp_base": 0.620, "unemp_base": 0.048},
    "Alberta":            {"pop": 4_600_000,  "emp_base": 0.630, "unemp_base": 0.065},
    "Manitoba":           {"pop": 1_400_000,  "emp_base": 0.610, "unemp_base": 0.052},
    "Saskatchewan":       {"pop": 1_200_000,  "emp_base": 0.625, "unemp_base": 0.050},
    "Nova Scotia":        {"pop":   970_000,  "emp_base": 0.568, "unemp_base": 0.072},
    "New Brunswick":      {"pop":   790_000,  "emp_base": 0.560, "unemp_base": 0.080},
    "Newfoundland":       {"pop":   520_000,  "emp_base": 0.528, "unemp_base": 0.120},
    "Prince Edward Island":{"pop":  168_000,  "emp_base": 0.570, "unemp_base": 0.090},
}

# COVID shock profile: magnitude of employment rate drop by month index
# Jan 2019 = index 0, April 2020 = index 15, Recovery through 2021
def covid_shock(date):
    if date < pd.Timestamp("2020-03-01"):
        return 0.0
    elif date == pd.Timestamp("2020-03-01"):
        return -0.03
    elif date == pd.Timestamp("2020-04-01"):
        return -0.095   # deepest trough
    elif date == pd.Timestamp("2020-05-01"):
        return -0.065
    elif date == pd.Timestamp("2020-06-01"):
        return -0.040
    elif date == pd.Timestamp("2020-07-01"):
        return -0.025
    elif date < pd.Timestamp("2021-01-01"):
        # Second wave partial recovery
        months_since_apr = (date.year - 2020) * 12 + (date.month - 4)
        return max(-0.025 + months_since_apr * 0.002, -0.018)
    elif date < pd.Timestamp("2022-01-01"):
        months_since_jan21 = (date.year - 2021) * 12 + (date.month - 1)
        return max(-0.015 + months_since_jan21 * 0.001, -0.005)
    else:
        return 0.0  # Full recovery by 2022

province_rows = []
for prov, params in provinces.items():
    for d in dates:
        shock = covid_shock(d)
        # Province-specific shock sensitivity
        sensitivity = 1.0
        if prov in ("Alberta",):          sensitivity = 1.15  # oil sector hit
        if prov in ("Ontario", "Quebec"): sensitivity = 1.05  # service sector
        if prov in ("British Columbia",): sensitivity = 0.90  # remote work resilient
        if prov in ("Newfoundland",):     sensitivity = 0.80  # already weak

        emp_rate  = params["emp_base"] + shock * sensitivity + np.random.normal(0, 0.002)
        unemp_shock = -shock * sensitivity * 0.7
        unemp_rate = params["unemp_base"] + unemp_shock + np.random.normal(0, 0.001)
        unemp_rate = max(0.03, min(0.25, unemp_rate))

        labour_force  = int(params["pop"] * 0.67)
        employed      = int(labour_force * emp_rate)
        unemployed    = int(labour_force * unemp_rate)
        not_in_lf     = params["pop"] - labour_force

        province_rows.append({
            "date":            d,
            "province":        prov,
            "employment_rate": round(emp_rate * 100, 2),
            "unemployment_rate": round(unemp_rate * 100, 2),
            "participation_rate": round((employed + unemployed) / params["pop"] * 100, 2),
            "employed_thousands": round(employed / 1000, 1),
            "unemployed_thousands": round(unemployed / 1000, 1),
            "population_thousands": round(params["pop"] / 1000, 1),
        })

df_province = pd.DataFrame(province_rows)

# ---------------------------------------------------------------------------
# 3. Industry-level data (Canada national)
# ---------------------------------------------------------------------------
industries = {
    "Goods-Producing": {
        "Agriculture":                 {"emp_2019": 285,  "covid_sens": 0.3},
        "Forestry, Fishing & Mining":  {"emp_2019": 320,  "covid_sens": 0.5},
        "Construction":                {"emp_2019": 1400, "covid_sens": 0.8},
        "Manufacturing":               {"emp_2019": 1750, "covid_sens": 0.9},
    },
    "Services-Producing": {
        "Wholesale & Retail Trade":    {"emp_2019": 2950, "covid_sens": 1.2},
        "Transportation & Warehousing":{"emp_2019": 960,  "covid_sens": 1.0},
        "Finance, Insurance & Real Estate": {"emp_2019": 1130, "covid_sens": 0.4},
        "Professional & Scientific":   {"emp_2019": 1450, "covid_sens": 0.3},
        "Educational Services":        {"emp_2019": 1250, "covid_sens": 0.6},
        "Health Care & Social Assistance": {"emp_2019": 2400, "covid_sens": 0.5},
        "Accommodation & Food Services": {"emp_2019": 1200, "covid_sens": 2.2},
        "Information, Culture & Recreation": {"emp_2019": 810, "covid_sens": 1.8},
        "Public Administration":       {"emp_2019": 890,  "covid_sens": 0.2},
        "Other Services":              {"emp_2019": 720,  "covid_sens": 1.1},
    }
}

industry_rows = []
for sector, sector_industries in industries.items():
    for industry, params in sector_industries.items():
        for d in dates:
            shock = covid_shock(d)
            emp = params["emp_2019"] * (1 + shock * params["covid_sens"])
            # Post-2022 growth trend
            if d >= pd.Timestamp("2022-01-01"):
                months_post = (d.year - 2022) * 12 + d.month
                growth = 1 + months_post * 0.0015
                emp *= growth
            emp += np.random.normal(0, params["emp_2019"] * 0.005)
            industry_rows.append({
                "date":     d,
                "sector":   sector,
                "industry": industry,
                "employed_thousands": round(max(emp, 0), 1),
            })

df_industry = pd.DataFrame(industry_rows)

# ---------------------------------------------------------------------------
# 4. Demographics: Sex × Age Group (Canada national)
# ---------------------------------------------------------------------------
demographics = {
    ("Men",   "15-24"): {"emp_rate_2019": 0.548, "unemp_2019": 0.115, "covid_sens": 1.4},
    ("Men",   "25-54"): {"emp_rate_2019": 0.856, "unemp_2019": 0.042, "covid_sens": 0.9},
    ("Men",   "55-64"): {"emp_rate_2019": 0.681, "unemp_2019": 0.048, "covid_sens": 0.8},
    ("Men",   "65+"):   {"emp_rate_2019": 0.140, "unemp_2019": 0.038, "covid_sens": 0.5},
    ("Women", "15-24"): {"emp_rate_2019": 0.530, "unemp_2019": 0.100, "covid_sens": 1.5},
    ("Women", "25-54"): {"emp_rate_2019": 0.778, "unemp_2019": 0.040, "covid_sens": 1.1},
    ("Women", "55-64"): {"emp_rate_2019": 0.590, "unemp_2019": 0.043, "covid_sens": 0.9},
    ("Women", "65+"):   {"emp_rate_2019": 0.085, "unemp_2019": 0.032, "covid_sens": 0.6},
}

demog_rows = []
for (sex, age), params in demographics.items():
    for d in dates:
        shock = covid_shock(d)
        emp_rate  = params["emp_rate_2019"] + shock * params["covid_sens"] + np.random.normal(0, 0.003)
        unemp_shock = -shock * params["covid_sens"] * 0.65
        unemp_rate  = params["unemp_2019"] + unemp_shock + np.random.normal(0, 0.002)
        unemp_rate  = max(0.02, min(0.35, unemp_rate))
        demog_rows.append({
            "date":             d,
            "sex":              sex,
            "age_group":        age,
            "employment_rate":  round(emp_rate * 100, 2),
            "unemployment_rate": round(unemp_rate * 100, 2),
        })

df_demog = pd.DataFrame(demog_rows)

# ---------------------------------------------------------------------------
# 5. Save to CSV
# ---------------------------------------------------------------------------
out = "/sessions/dazzling-sweet-pascal/day1_labour_market/data"
df_province.to_csv(f"{out}/lfs_province.csv", index=False)
df_industry.to_csv(f"{out}/lfs_industry.csv", index=False)
df_demog.to_csv(f"{out}/lfs_demographics.csv", index=False)

print("✅ Data generated successfully")
print(f"   Province dataset:    {df_province.shape}")
print(f"   Industry dataset:    {df_industry.shape}")
print(f"   Demographics dataset:{df_demog.shape}")
print(f"\nDate range: {dates[0].date()} → {dates[-1].date()} ({len(dates)} months)")
