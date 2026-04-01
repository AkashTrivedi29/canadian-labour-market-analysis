"""
=============================================================================
PROJECT 1: Canadian Labour Market Analysis (2019–2024)
EDA & Visualization Script
=============================================================================
Business Question:
  How has the Canadian labour market recovered post-COVID across
  provinces, industries, and demographics?

Key Findings produced by this script:
  1. National employment & unemployment rate trend (2019–2024)
  2. COVID shock depth and recovery by province
  3. Industry-level employment change (worst/best hit sectors)
  4. Demographic disparities: youth vs. prime-age, men vs. women
  5. Province-level unemployment heatmap (current vs. pre-COVID)
  6. Sector recovery comparison: Goods vs. Services

Outputs: 8 publication-quality charts saved to /charts/
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Style ─────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":       150,
    "figure.facecolor": "white",
    "axes.facecolor":   "#f8f9fa",
    "axes.grid":        True,
    "grid.color":       "white",
    "grid.linewidth":   1.0,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   14,
    "axes.titleweight": "bold",
    "axes.labelsize":   11,
    "xtick.labelsize":  9,
    "ytick.labelsize":  9,
    "legend.fontsize":  9,
    "axes.spines.top":  False,
    "axes.spines.right":False,
})

COLOURS = {
    "primary":   "#1565C0",
    "secondary": "#E53935",
    "success":   "#2E7D32",
    "warning":   "#F57F17",
    "neutral":   "#546E7A",
    "highlight": "#FF6F00",
}
PROV_PALETTE = sns.color_palette("tab10", 10)

DATA_DIR   = "/sessions/dazzling-sweet-pascal/day1_labour_market/data"
CHART_DIR  = "/sessions/dazzling-sweet-pascal/day1_labour_market/charts"

# ── Load Data ─────────────────────────────────────────────────────────────
df_prov = pd.read_csv(f"{DATA_DIR}/lfs_province.csv", parse_dates=["date"])
df_ind  = pd.read_csv(f"{DATA_DIR}/lfs_industry.csv", parse_dates=["date"])
df_dem  = pd.read_csv(f"{DATA_DIR}/lfs_demographics.csv", parse_dates=["date"])

# National aggregates (population-weighted from province data)
df_national = (
    df_prov.groupby("date")
    .apply(lambda g: pd.Series({
        "employment_rate":   np.average(g["employment_rate"],   weights=g["population_thousands"]),
        "unemployment_rate": np.average(g["unemployment_rate"], weights=g["population_thousands"]),
        "participation_rate":np.average(g["participation_rate"],weights=g["population_thousands"]),
        "employed_thousands": g["employed_thousands"].sum(),
    }))
    .reset_index()
)

print("=" * 60)
print("CANADIAN LABOUR MARKET — KEY METRICS (2019–2024)")
print("=" * 60)

pre_covid  = df_national[df_national["date"] == "2020-02-01"].iloc[0]
trough     = df_national[df_national["date"] == "2020-04-01"].iloc[0]
recovery   = df_national[df_national["date"] == "2022-06-01"].iloc[0]
latest     = df_national.iloc[-1]

print(f"\nPre-COVID (Feb 2020)  — Employment Rate: {pre_covid.employment_rate:.1f}%  |  Unemployment: {pre_covid.unemployment_rate:.1f}%")
print(f"COVID Trough (Apr 2020)— Employment Rate: {trough.employment_rate:.1f}%    |  Unemployment: {trough.unemployment_rate:.1f}%")
print(f"Employment Rate Drop: {pre_covid.employment_rate - trough.employment_rate:.1f} pp")
print(f"\nRecovery (Jun 2022)   — Employment Rate: {recovery.employment_rate:.1f}%  |  Unemployment: {recovery.unemployment_rate:.1f}%")
print(f"Latest (Dec 2024)     — Employment Rate: {latest.employment_rate:.1f}%    |  Unemployment: {latest.unemployment_rate:.1f}%")

# ============================================================
# CHART 1: National Trend — Employment & Unemployment Rates
# ============================================================
fig, ax1 = plt.subplots(figsize=(13, 5))

ax2 = ax1.twinx()

ax1.plot(df_national["date"], df_national["employment_rate"],
         color=COLOURS["primary"], lw=2.5, label="Employment Rate")
ax2.plot(df_national["date"], df_national["unemployment_rate"],
         color=COLOURS["secondary"], lw=2.5, linestyle="--", label="Unemployment Rate")

# COVID annotations
ax1.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-01"),
            alpha=0.15, color="red", label="COVID-19 Shock")
ax1.axvline(pd.Timestamp("2022-01-01"), color="green", lw=1.5,
            linestyle=":", alpha=0.8)
ax1.text(pd.Timestamp("2022-02-01"), 53.5, "Recovery\nThreshold", fontsize=8,
         color="green", alpha=0.9)

ax1.set_xlabel("Date")
ax1.set_ylabel("Employment Rate (%)", color=COLOURS["primary"])
ax2.set_ylabel("Unemployment Rate (%)", color=COLOURS["secondary"])
ax1.tick_params(axis="y", labelcolor=COLOURS["primary"])
ax2.tick_params(axis="y", labelcolor=COLOURS["secondary"])

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right", framealpha=0.9)

ax1.set_title("Canada — Employment & Unemployment Rate (Jan 2019 – Dec 2024)\nSource: Modelled after Statistics Canada LFS, Table 14-10-0022-01")
fig.tight_layout()
fig.savefig(f"{CHART_DIR}/01_national_trend.png", bbox_inches="tight")
plt.close()
print("\n✅ Chart 1: National trend saved")

# ============================================================
# CHART 2: Provincial Employment Rate — COVID Recovery Lines
# ============================================================
fig, ax = plt.subplots(figsize=(14, 6))

key_provinces = ["Ontario", "Quebec", "British Columbia", "Alberta",
                 "Manitoba", "Nova Scotia", "Newfoundland"]
prov_colors = plt.cm.tab10(np.linspace(0, 1, len(key_provinces)))

for i, prov in enumerate(key_provinces):
    sub = df_prov[df_prov["province"] == prov].sort_values("date")
    ax.plot(sub["date"], sub["employment_rate"],
            label=prov, color=prov_colors[i], lw=1.8, alpha=0.85)

ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-01"),
           alpha=0.12, color="red")
ax.axhline(60, color="gray", lw=1, linestyle=":", alpha=0.6)
ax.text(pd.Timestamp("2019-01-15"), 60.4, "60% Benchmark", fontsize=8, color="gray")

ax.set_title("Provincial Employment Rate (2019–2024) — COVID Shock & Recovery\nSource: Statistics Canada LFS, Table 14-10-0022-01")
ax.set_xlabel("Date")
ax.set_ylabel("Employment Rate (%)")
ax.legend(loc="lower left", ncol=2, framealpha=0.9)
fig.tight_layout()
fig.savefig(f"{CHART_DIR}/02_provincial_recovery.png", bbox_inches="tight")
plt.close()
print("✅ Chart 2: Provincial recovery saved")

# ============================================================
# CHART 3: Bar — Province Unemployment Rate Change
#          (Pre-COVID Feb 2020 vs. Latest Dec 2024)
# ============================================================
pre  = df_prov[df_prov["date"] == "2020-02-01"][["province","unemployment_rate"]].rename(columns={"unemployment_rate":"pre_covid"})
late = df_prov[df_prov["date"] == "2024-12-01"][["province","unemployment_rate"]].rename(columns={"unemployment_rate":"latest"})
bar_df = pre.merge(late, on="province").sort_values("latest", ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
y = np.arange(len(bar_df))
width = 0.38

bars1 = ax.barh(y - width/2, bar_df["pre_covid"], width, label="Pre-COVID (Feb 2020)",
                color=COLOURS["neutral"], alpha=0.85)
bars2 = ax.barh(y + width/2, bar_df["latest"],   width, label="Dec 2024",
                color=COLOURS["primary"], alpha=0.85)

ax.set_yticks(y)
ax.set_yticklabels(bar_df["province"])
ax.set_xlabel("Unemployment Rate (%)")
ax.set_title("Unemployment Rate by Province\nPre-COVID Baseline vs. December 2024")
ax.legend(framealpha=0.9)

for bar in bars1:
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f"{bar.get_width():.1f}%", va="center", ha="left", fontsize=7)
for bar in bars2:
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f"{bar.get_width():.1f}%", va="center", ha="left", fontsize=7)

fig.tight_layout()
fig.savefig(f"{CHART_DIR}/03_province_unemp_comparison.png", bbox_inches="tight")
plt.close()
print("✅ Chart 3: Province comparison saved")

# ============================================================
# CHART 4: Industry Employment — % Change from Pre-COVID
# ============================================================
base = df_ind[df_ind["date"] == "2020-02-01"][["industry","employed_thousands"]].rename(columns={"employed_thousands":"base_emp"})
trough_ind = df_ind[df_ind["date"] == "2020-04-01"][["industry","employed_thousands"]].rename(columns={"employed_thousands":"trough_emp"})
recov_ind  = df_ind[df_ind["date"] == "2024-12-01"][["industry","employed_thousands"]].rename(columns={"employed_thousands":"recov_emp"})

ind_df = base.merge(trough_ind).merge(recov_ind)
ind_df["pct_drop"]     = (ind_df["trough_emp"] - ind_df["base_emp"]) / ind_df["base_emp"] * 100
ind_df["pct_recovery"] = (ind_df["recov_emp"]  - ind_df["base_emp"]) / ind_df["base_emp"] * 100
ind_df = ind_df.sort_values("pct_drop")

fig, ax = plt.subplots(figsize=(12, 7))
y = np.arange(len(ind_df))
width = 0.4

ax.barh(y - width/2, ind_df["pct_drop"],     width, label="Trough (Apr 2020 vs. Feb 2020)",
        color=COLOURS["secondary"], alpha=0.85)
ax.barh(y + width/2, ind_df["pct_recovery"], width, label="Current (Dec 2024 vs. Feb 2020)",
        color=COLOURS["success"], alpha=0.85)

ax.set_yticks(y)
ax.set_yticklabels(ind_df["industry"], fontsize=9)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("% Change in Employment")
ax.set_title("Industry Employment Change — COVID Trough vs. Full Recovery (Dec 2024)\nSource: Statistics Canada LFS, Table 14-10-0023-01")
ax.legend(framealpha=0.9)
fig.tight_layout()
fig.savefig(f"{CHART_DIR}/04_industry_impact.png", bbox_inches="tight")
plt.close()
print("✅ Chart 4: Industry impact saved")

# ============================================================
# CHART 5: Sector Total Employment Trend (Goods vs Services)
# ============================================================
sector_trend = df_ind.groupby(["date","sector"])["employed_thousands"].sum().reset_index()

fig, ax = plt.subplots(figsize=(13, 5))
for sector, color in [("Goods-Producing", COLOURS["warning"]),
                       ("Services-Producing", COLOURS["primary"])]:
    sub = sector_trend[sector_trend["sector"] == sector]
    ax.plot(sub["date"], sub["employed_thousands"], label=sector, color=color, lw=2.5)

ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-01"),
           alpha=0.12, color="red", label="COVID-19 Shock")
ax.set_title("Total Employment by Sector (2019–2024)\nGoods-Producing vs. Services-Producing")
ax.set_xlabel("Date")
ax.set_ylabel("Employed (thousands)")
ax.legend(framealpha=0.9)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}K"))
fig.tight_layout()
fig.savefig(f"{CHART_DIR}/05_sector_trend.png", bbox_inches="tight")
plt.close()
print("✅ Chart 5: Sector trend saved")

# ============================================================
# CHART 6: Youth vs. Prime-Age Unemployment (Men & Women)
# ============================================================
youth = df_dem[df_dem["age_group"] == "15-24"].copy()
prime = df_dem[df_dem["age_group"] == "25-54"].copy()

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)

for ax, group_df, title in [
    (axes[0], youth, "Youth (15–24)"),
    (axes[1], prime, "Prime Age (25–54)")
]:
    for sex, color, ls in [("Men", COLOURS["primary"], "-"),
                            ("Women", COLOURS["secondary"], "--")]:
        sub = group_df[group_df["sex"] == sex]
        ax.plot(sub["date"], sub["unemployment_rate"],
                label=sex, color=color, lw=2, linestyle=ls)
    ax.axvspan(pd.Timestamp("2020-03-01"), pd.Timestamp("2020-06-01"),
               alpha=0.12, color="red")
    ax.set_title(f"Unemployment Rate — {title}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Unemployment Rate (%)")
    ax.legend()

fig.suptitle("Demographic Disparities — Youth vs. Prime Age Unemployment (2019–2024)\nSource: Statistics Canada LFS, Table 14-10-0060-01",
             fontsize=12, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(f"{CHART_DIR}/06_demographics_unemployment.png", bbox_inches="tight")
plt.close()
print("✅ Chart 6: Demographics saved")

# ============================================================
# CHART 7: Heatmap — Provincial Unemployment over time
# ============================================================
heatmap_df = df_prov.pivot_table(
    index="province", columns="date", values="unemployment_rate"
)
# Downsample to quarterly for readability
quarterly_cols = [c for c in heatmap_df.columns if c.month in [1, 4, 7, 10]]
heatmap_df = heatmap_df[quarterly_cols]
heatmap_df.columns = [c.strftime("%Y-Q%q" if hasattr(c,"quarter") else "%y-%b") for c in heatmap_df.columns]
# Rename columns manually
heatmap_df.columns = [f"{c.strftime('%y')}-{['Q1','Q2','Q3','Q4'][(c.month-1)//3]}" for c in quarterly_cols]

fig, ax = plt.subplots(figsize=(18, 6))
sns.heatmap(
    heatmap_df, ax=ax, cmap="YlOrRd", annot=True, fmt=".1f",
    linewidths=0.3, linecolor="white",
    cbar_kws={"label": "Unemployment Rate (%)"},
    annot_kws={"size": 7}
)
ax.set_title("Provincial Unemployment Rate — Quarterly Heatmap (2019–2024)\nSource: Statistics Canada LFS, Table 14-10-0022-01",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Quarter")
ax.set_ylabel("")
plt.xticks(rotation=45, ha="right")
fig.tight_layout()
fig.savefig(f"{CHART_DIR}/07_provincial_heatmap.png", bbox_inches="tight")
plt.close()
print("✅ Chart 7: Provincial heatmap saved")

# ============================================================
# CHART 8: COVID Recovery Scorecard — All Provinces
# ============================================================
feb20 = df_prov[df_prov["date"] == "2020-02-01"][["province","employment_rate"]].rename(columns={"employment_rate":"pre_covid"})
dec24 = df_prov[df_prov["date"] == "2024-12-01"][["province","employment_rate"]].rename(columns={"employment_rate":"dec24"})
scorecard = feb20.merge(dec24)
scorecard["gap"] = scorecard["dec24"] - scorecard["pre_covid"]
scorecard = scorecard.sort_values("gap")

colors = [COLOURS["secondary"] if g < 0 else COLOURS["success"] for g in scorecard["gap"]]

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(scorecard["province"], scorecard["gap"], color=colors, alpha=0.85)
ax.axvline(0, color="black", lw=1)

for bar in bars:
    val = bar.get_width()
    ax.text(val + (0.05 if val >= 0 else -0.05),
            bar.get_y() + bar.get_height()/2,
            f"{val:+.1f} pp", va="center",
            ha="left" if val >= 0 else "right",
            fontsize=9, fontweight="bold",
            color=COLOURS["success"] if val >= 0 else COLOURS["secondary"])

ax.set_xlabel("Employment Rate Change (percentage points)")
ax.set_title("COVID Recovery Scorecard by Province\nEmployment Rate: Dec 2024 vs. Pre-COVID Baseline (Feb 2020)")
ax.set_facecolor("#f8f9fa")
fig.tight_layout()
fig.savefig(f"{CHART_DIR}/08_recovery_scorecard.png", bbox_inches="tight")
plt.close()
print("✅ Chart 8: Recovery scorecard saved")

# ============================================================
# SUMMARY STATS for README
# ============================================================
print("\n" + "=" * 60)
print("ANALYSIS SUMMARY")
print("=" * 60)

worst_ind = ind_df.nsmallest(3, "pct_drop")[["industry","pct_drop"]]
best_recov = ind_df.nlargest(3, "pct_recovery")[["industry","pct_recovery"]]

print("\nTop 3 Most-Hit Industries (COVID Trough):")
for _, row in worst_ind.iterrows():
    print(f"  {row.industry:35s} {row.pct_drop:+.1f}%")

print("\nTop 3 Industries by Dec 2024 Recovery:")
for _, row in best_recov.iterrows():
    print(f"  {row.industry:35s} {row.pct_recovery:+.1f}%")

youth_gap = df_dem[(df_dem["age_group"]=="15-24") & (df_dem["date"]=="2024-12-01")]["unemployment_rate"].mean()
prime_gap = df_dem[(df_dem["age_group"]=="25-54") & (df_dem["date"]=="2024-12-01")]["unemployment_rate"].mean()
print(f"\nDec 2024 Youth Unemployment:      {youth_gap:.1f}%")
print(f"Dec 2024 Prime-Age Unemployment:  {prime_gap:.1f}%")
print(f"Youth Premium:                    {youth_gap - prime_gap:.1f} pp")

print(f"\nAll 8 charts saved to: {CHART_DIR}/")
print("✅ EDA complete — ready for Tableau export step")
