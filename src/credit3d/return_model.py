from dataclasses import dataclass
from typing import Optional
import math

from .curves import interpolate_sector_oas, interpolate_rf, sector_slope_bps_per_year
from .risk import ytm_from_price, modified_duration, dv01

# Simple rating-to-PD mapping (annual) for demo purposes
RATING_PD = {
    "AAA": 0.0001,
    "AA": 0.0002,
    "A": 0.0005,
    "BBB": 0.0020
}

def rating_bucket(r: str) -> str:
    r = r.upper()
    if r.startswith("AAA"): return "AAA"
    if r.startswith("AA"): return "AA"
    if r.startswith("A"): return "A"
    return "BBB"

def lgd_by_seniority(seniority: str) -> float:
    s = (seniority or "").lower()
    if "covered" in s: return 0.4
    if "secured" in s: return 0.45
    if "tier2" in s or "sub" in s: return 0.65
    return 0.6  # senior unsecured default

@dataclass
class ReturnMetrics:
    ytm: float
    bond_oas_bps: float
    sector_oas_bps: float
    fair_value_gap_bps: float
    carry_bps: float
    rolldown_bps: float
    expected_delta_oas_bps: float
    expected_return_pct: float
    expected_loss_pct: float

def compute_return_metrics(row, curves_df, funding_rate: float, horizon_months: int = 6, mispricing_convergence: float = 0.3) -> ReturnMetrics:
    # Inputs
    price = float(row["price"])
    coupon = float(row["coupon"])
    maturity_years = float(row["tenor_years"])
    freq = 2  # semi-annual
    face = 100.0
    
    # YTM
    ytm = ytm_from_price(price, face, coupon, freq, maturity_years)
    
    # OAS approximations
    rf = interpolate_rf(curves_df, maturity_years)
    bond_oas_bps = (ytm - rf) * 10000.0
    sector_oas_bps = interpolate_sector_oas(curves_df, row["sector"], row["rating"], maturity_years)
    fair_value_gap_bps = bond_oas_bps - sector_oas_bps
    
    # Carry & rolldown (very simple demo approximations)
    carry_bps = (ytm - funding_rate) * 10000.0
    slope = sector_slope_bps_per_year(curves_df, row["sector"], row["rating"], maturity_years)
    rolldown_bps = -slope * (horizon_months/12.0)  # if curve downward with tenor, positive rolldown
    
    expected_delta_oas_bps = - mispricing_convergence * fair_value_gap_bps  # partial convergence
    
    # Convert spread change to price effect via DV01
    mod_dur = modified_duration(price, face, coupon, freq, ytm, maturity_years)
    dv = dv01(price, mod_dur)  # price change per 1bp
    price_effect_pct = (dv * expected_delta_oas_bps) / price  # percent of price
    
    # Carry as % of price for horizon (approximate simple accrual)
    carry_pct = (carry_bps/10000.0) * (horizon_months/12.0)
    rolldown_pct = (rolldown_bps/10000.0) * (dv/price)  # translate bps move to % via DV01
    
    # Expected loss over horizon from PD*LGD
    pd_annual = RATING_PD.get(rating_bucket(row["rating"]), 0.003)
    lgd = lgd_by_seniority(row.get("seniority",""))
    pd_horizon = 1 - (1 - pd_annual)**(horizon_months/12.0)
    expected_loss_pct = pd_horizon * lgd
    
    expected_return_pct = carry_pct + rolldown_pct + price_effect_pct - expected_loss_pct
    
    return ReturnMetrics(
        ytm=ytm,
        bond_oas_bps=bond_oas_bps,
        sector_oas_bps=sector_oas_bps,
        fair_value_gap_bps=fair_value_gap_bps,
        carry_bps=carry_bps,
        rolldown_bps=rolldown_bps,
        expected_delta_oas_bps=expected_delta_oas_bps,
        expected_return_pct=expected_return_pct,
        expected_loss_pct=expected_loss_pct
    )
