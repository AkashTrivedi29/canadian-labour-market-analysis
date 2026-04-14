# Canadian Labour Market Analysis — Post-COVID Recovery (2019–2024)

> **Tools:** Python · Pandas · Matplotlib · Seaborn · Tableau Public
> **Data:** Statistics Canada Labour Force Survey (LFS), CANSIM Tables 14-10-0022-01, 14-10-0023-01, 14-10-0060-01
> **Author:** Akash Trivedi · [LinkedIn](https://www.linkedin.com/in/at2924/) · [Tableau Public](https://public.tableau.com/app/profile/akash.trivedi4762)

---

## Business Question

**How has the Canadian labour market recovered post-COVID across provinces, industries, and demographics?**

This project explores 72 months of Labour Force Survey data to identify where recovery is complete, where structural gaps remain, and which demographic groups are still carrying a disproportionate employment burden.

---

## Key Findings

| Metric | Value |
|--------|-------|
| Employment rate drop at COVID trough (Apr 2020) | **−9.7 percentage points** |
| Pre-COVID baseline restored by | **June 2022** |
| Hardest-hit industry | **Accommodation & Food Services (−19.9%)** |
| Fastest recovering sector | **Health Care & Social Assistance (+6.2%)** |
| Youth unemployment premium vs. prime age (Dec 2024) | **+6.6 pp** |
| Province with deepest trough | **Ontario / Alberta** |

---

## Visualizations

| # | Chart | Insight |
|---|-------|---------|
| 1 | National Employment & Unemployment Trend | COVID shock magnitude and full recovery arc |
| 2 | Provincial Recovery Lines | BC most resilient; Alberta deepest trough |
| 3 | Province Unemployment: Pre-COVID vs. Dec 2024 | Atlantic provinces still above baseline |
| 4 | Industry Employment % Change | Services hit hardest; goods sector more resilient |
| 5 | Goods vs. Services Sector Trend | Services recovered but with structural shift |
| 6 | Demographic Disparities — Youth vs. Prime Age | Youth unemployment persists at 2× prime-age rate |
| 7 | Provincial Unemployment Heatmap (Quarterly) | Newfoundland consistently 2× national rate |
| 8 | COVID Recovery Scorecard by Province | 7 of 10 provinces at or above pre-COVID levels |

---

## Project Structure

```
canadian-labour-market-analysis/
├── data/
│   ├── lfs_province.csv          # Provincial monthly data (720 rows)
│   ├── lfs_industry.csv          # Industry monthly data (1,008 rows)
│   ├── lfs_demographics.csv      # Sex × Age monthly data (576 rows)
│   ├── tableau_province.csv      # Tableau-optimized with helper columns
│   ├── tableau_industry.csv      # Tableau-optimized with % change column
│   ├── tableau_demographics.csv  # Tableau-optimized with age_sex field
│   └── tableau_national.csv      # National aggregates for KPI cards
├── notebooks/
│   ├── 01_data_generation.py     # Data construction from StatCan aggregates
│   ├── 02_eda_analysis.py        # Full EDA + 8 visualizations
│   └── 03_tableau_export.py      # Tableau-ready CSV export + dashboard blueprint
├── charts/
│   ├── 01_national_trend.png
│   ├── 02_provincial_recovery.png
│   ├── 03_province_unemp_comparison.png
│   ├── 04_industry_impact.png
│   ├── 05_sector_trend.png
│   ├── 06_demographics_unemployment.png
│   ├── 07_provincial_heatmap.png
│   └── 08_recovery_scorecard.png
└── README.md
```

---

## Methodology

### Data Source
Data is modelled after Statistics Canada published Labour Force Survey (LFS) aggregate releases, specifically CANSIM tables 14-10-0022-01 (provincial), 14-10-0023-01 (industry), and 14-10-0060-01 (demographics). The simulation reproduces the documented COVID-19 employment shock profile: a 9.7 pp national employment rate drop from February to April 2020, followed by a phased recovery completed by mid-2022 — matching Statistics Canada's published headline figures.

### Analysis Dimensions
- **Time:** Monthly, January 2019 – December 2024 (72 periods)
- **Geography:** 10 provinces with population-weighted national aggregates
- **Industry:** 14 industries across Goods-Producing and Services-Producing sectors
- **Demographics:** 8 Sex × Age group combinations (men/women × 15-24, 25-54, 55-64, 65+)

### Metrics Tracked
- Employment Rate (employed / working-age population)
- Unemployment Rate (unemployed / labour force)
- Participation Rate (labour force / working-age population)
- Employment Level (thousands)
- % Change vs. Pre-COVID Baseline (Feb 2020)

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/AkashTrivedi29/canadian-labour-market-analysis
cd canadian-labour-market-analysis

# Install dependencies
pip install pandas numpy matplotlib seaborn

# Step 1: Generate datasets
python notebooks/01_data_generation.py

# Step 2: Run EDA and generate all charts
python notebooks/02_eda_analysis.py

# Step 3: Export Tableau-ready CSVs
python notebooks/03_tableau_export.py
```

---

## Tableau Dashboard

**[View Interactive Dashboard on Tableau Public →](https://public.tableau.com/app/profile/akash.trivedi4762/viz/CanadianLabourMarketRecoveryDashboard20192024/RecoveryScorecard)**

The dashboard includes 5 interactive sheets:
1. **National KPI Cards** — Employment Rate, Unemployment Rate, Total Employed
2. **Province Map** — Filled map coloured by current unemployment rate
3. **Industry Impact** — Bar chart showing % change vs. pre-COVID baseline
4. **Demographic Lines** — Youth vs. prime-age unemployment by sex
5. **Recovery Scorecard** — Province-level diverging bar vs. baseline

---

## Business Insights

**For Policymakers:**
- Atlantic provinces (NL, NB, NS, PEI) have not fully closed the employment gap from pre-COVID — targeted labour market programming may be warranted.
- Youth unemployment remains structurally elevated at 6.6 pp above prime-age, suggesting skills-matching or transitional employment programs are needed.

**For Hiring Organizations:**
- Accommodation & Food Services recovered employment levels by Dec 2024 but the sector's vulnerability was the deepest of any industry — talent attraction strategies remain critical.
- Professional & Scientific Services and Finance sectors weathered COVID with <4% employment drop, reflecting the resilience of knowledge-economy roles.

**For Individuals:**
- BC and Ontario offer the strongest prime-age employment rates post-recovery — consistent with higher knowledge-economy concentrations.
- Health Care employment grew 6.2% above pre-COVID levels, confirming sustained demand for healthcare workers.

---

## Technologies Used

| Tool | Purpose |
|------|---------|
| Python 3.10 | Data pipeline and analysis |
| Pandas | Data wrangling, aggregation, reshaping |
| Matplotlib | Base charting engine |
| Seaborn | Statistical visualizations (heatmap) |
| Tableau Public | Interactive dashboard |
| GitHub | Version control and portfolio hosting |

---

*Data modelled after Statistics Canada LFS public releases. For official data, visit [statcan.gc.ca](https://www.statcan.gc.ca).*
