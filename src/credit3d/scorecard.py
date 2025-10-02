from dataclasses import dataclass, asdict
from typing import Dict

from .risk import modified_duration, dv01, krd_vector, liquidity_bucket, shock_pl
from .return_model import compute_return_metrics
from .sust import compute_sust_metrics

@dataclass
class Scorecard:
    isin: str
    issuer: str
    sector: str
    rating: str
    seniority: str
    tenor_years: float
    price: float
    risk: Dict
    ret: Dict
    sust: Dict
    mandate_fit: str

def compute_scorecard(row, curves_df, funding_rate: float, horizon_months: int, mandate: str) -> Scorecard:
    price = float(row["price"])
    face = 100.0
    coupon = float(row["coupon"])
    tenor = float(row["tenor_years"])
    freq = 2
    
    # Risk
    # We recompute ytm via return module (consistent), then duration/DV01 using that ytm
    rm = compute_return_metrics(row, curves_df, funding_rate, horizon_months)
    mod_dur = modified_duration(price, face, coupon, freq, rm.ytm, tenor)
    dv = dv01(price, mod_dur)
    krd = krd_vector(dv, tenor)
    liq = liquidity_bucket(float(row.get("issue_size_mil", 0)))
    pl_50 = shock_pl(price, dv, 50) / price
    pl_100 = shock_pl(price, dv, 100) / price
    
    risk = {
        "mod_duration": round(mod_dur, 3),
        "dv01_per_100": round(dv, 4),
        "krd": {str(k): round(v,4) for k,v in krd.items()},
        "liquidity_bucket": liq,
        "shock_pl_pct_50bps": round(pl_50, 4),
        "shock_pl_pct_100bps": round(pl_100, 4)
    }
    
    # Return
    ret = {
        "ytm": round(rm.ytm, 4),
        "bond_oas_bps": round(rm.bond_oas_bps, 1),
        "sector_oas_bps": round(rm.sector_oas_bps, 1),
        "fair_value_gap_bps": round(rm.fair_value_gap_bps, 1),
        "carry_bps": round(rm.carry_bps, 1),
        "rolldown_bps": round(rm.rolldown_bps, 1),
        "expected_delta_oas_bps": round(rm.expected_delta_oas_bps, 1),
        "expected_return_pct": round(rm.expected_return_pct, 3),
        "expected_loss_pct": round(rm.expected_loss_pct, 3)
    }
    
    # Sustainability
    sm = compute_sust_metrics(row)
    sust = {
        "score": sm.score,
        "trajectory": sm.trajectory,
        "material": sm.material
    }
    
    # Mandate fit
    # Protection (Euro IG): EUR currency and rating bucket in IG; neutral exclude AT1
    mand = "Global"
    if mandate.lower().startswith("protect"):
        if (row.get("currency","EUR") == "EUR") and (row.get("rating","BBB")[:1] in ["A","B"] or row.get("rating","AAA").startswith("AA") or row.get("rating","AAA").startswith("AAA")):
            if "at1" not in str(row.get("seniority","")).lower():
                mand = "Protection"
    else:
        mand = "Global"
    
    return Scorecard(
        isin=row["isin"],
        issuer=row["issuer"],
        sector=row["sector"],
        rating=row["rating"],
        seniority=row.get("seniority",""),
        tenor_years=float(row["tenor_years"]),
        price=float(row["price"]),
        risk=risk,
        ret=ret,
        sust=sust,
        mandate_fit=mand
    )
