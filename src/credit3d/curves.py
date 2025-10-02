import numpy as np
import pandas as pd

def _pick_bucket(rating: str) -> str:
    # Map ratings to broad buckets
    if rating.upper().startswith('AAA'): return 'AAA'
    if rating.upper().startswith('AA'): return 'AA'
    if rating.upper().startswith('A'): return 'A'
    return 'BBB'

def interpolate_sector_oas(curves_df: pd.DataFrame, sector: str, rating: str, tenor_years: float) -> float:
    bucket = _pick_bucket(rating)
    sub = curves_df[(curves_df['sector'] == sector) & (curves_df['rating_bucket'] == bucket)].copy()
    if sub.empty:
        # fallback: any sector with same bucket
        sub = curves_df[curves_df['rating_bucket'] == bucket].copy()
    sub = sub.sort_values('tenor_years')
    x = sub['tenor_years'].values
    y = sub['sector_oas_bps'].values
    return float(np.interp(tenor_years, x, y))

def interpolate_rf(curves_df: pd.DataFrame, tenor_years: float) -> float:
    # use all rows irrespective of sector; assume rf is common
    sub = curves_df[['tenor_years','rf_rate']].drop_duplicates().sort_values('tenor_years')
    return float(np.interp(tenor_years, sub['tenor_years'].values, sub['rf_rate'].values))

def sector_slope_bps_per_year(curves_df: pd.DataFrame, sector: str, rating: str, tenor_years: float) -> float:
    # finite difference slope of OAS curve around tenor
    bucket = _pick_bucket(rating)
    sub = curves_df[(curves_df['sector'] == sector) & (curves_df['rating_bucket'] == bucket)].copy().sort_values('tenor_years')
    x = sub['tenor_years'].values
    y = sub['sector_oas_bps'].values
    if len(x) < 2:
        return 0.0
    # Use central difference where possible
    idx = np.searchsorted(x, tenor_years)
    if idx == 0:
        i, j = 0, 1
    elif idx >= len(x):
        i, j = len(x)-2, len(x)-1
    else:
        i, j = idx-1, idx
    dx = x[j]-x[i]
    dy = y[j]-y[i]
    return float(dy/dx) if dx != 0 else 0.0
