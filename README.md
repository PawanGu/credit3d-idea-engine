# 3D Credit Idea Engine (Euro IG Financials)

**Purpose:** Generate bond-level **trade ideas** for Euro Investment Grade (Financials) with a compact **Risk–Return–Sustainability** scorecard and a simple **mandate fit** flag (Protection Credit vs. Global Credit).

### Three dimensions (how it's implemented)
- **Risk:** Modified duration, DV01, simple **key-rate duration** (weights), liquidity proxy, base ±50/±100 bps spread shock P/L.
- **Return:** Carry (YTM − funding), rolldown (slope of sector OAS curve), **fair-value gap** (bond OAS vs. sector OAS), expected return that combines carry + rolldown + partial gap convergence − expected loss.
- **Sustainability:** Sector‑material metrics by issuer (banks/insurers/real estate) turned into a 0–1 score plus **trajectory** tags (improving/flat/deteriorating).

> This repo uses **small stub CSVs** in `/data` so everything runs locally without vendor data.

## Quickstart
```bash
pip install -r requirements.txt
python -m credit3d.cli --data_dir ./data --horizon_months 6 --funding_rate 0.02 --mandate protection
# Output: reports/ideas_YYYYMMDD_HHMM.md
```

## Data model
- `data/bonds.csv` — universe of bonds (Euro IG financials). Sample columns:
  `isin,issuer,sector,rating,maturity_yyyy_mm_dd,coupon,price,issue_size_mil,currency,seniority,country`
- `data/curves.csv` — sector OAS and risk‑free rates by tenor:
  `sector,rating_bucket,tenor_years,sector_oas_bps,rf_rate`
- `data/kpi_issuers.csv` — issuer-level KPIs & sustainability flags (combined banks/insurers/RE):
  `issuer,sector,cet1,lcr,nsfr,solvency_coverage,ltv,icr,green_lending_pct,coal_exposure_pct,controversies,trajectory`

## Outputs
- **Markdown** idea report in `/reports` with one **scorecard** per bond:
  - **Risk:** ΣKRD (weights), DV01, Liquidity bucket
  - **Return:** Carry, Rolldown, ΔOAS·DV01 (convergence), Expected Return (horizon)
  - **Sustainability:** Score (0–1), material factors, trajectory
  - **Mandate fit:** Protection (Euro IG) / Global

## Structure
```
src/credit3d/
  __init__.py
  dataio.py
  curves.py
  risk.py
  return_model.py
  sust.py
  scorecard.py
  idea_card.py
  cli.py
data/
  bonds.csv
  curves.csv
  kpi_issuers.csv
reports/
tests/
  test_risk.py
  test_scorecard.py
notebooks/
  issuer_screen.ipynb
```

## Notes
- This is a **teaching/demo** project. Numbers are illustrative.
- Feel free to replace CSVs with public data and expand tests.
