from dataclasses import dataclass
from typing import Dict

@dataclass
class SustMetrics:
    score: float
    trajectory: str
    material: Dict[str, float]

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def _norm(x, lo, hi):
    if x is None: return 0.5
    try:
        x = float(x)
    except Exception:
        return 0.5
    if hi == lo: return 0.5
    v = (x - lo)/(hi - lo)
    return clamp01(v)

def compute_sust_metrics(row) -> SustMetrics:
    sector = (row.get("sector","") or "").lower()
    traj = row.get("trajectory", "flat")
    material = {}
    score = 0.5
    
    if "bank" in sector:
        coal = float(row.get("coal_exposure_pct", 0) or 0)
        green = float(row.get("green_lending_pct", 0) or 0)
        material = {"coal_exposure_pct": coal, "green_lending_pct": green}
        score = 0.6 * (1 - _norm(coal, 0, 30)) + 0.4 * _norm(green, 0, 50)
    elif "insur" in sector:
        solv = float(row.get("solvency_coverage", 150) or 150)
        material = {"solvency_coverage": solv}
        score = _norm(solv, 100, 250)
    elif "real" in sector:
        ltv = float(row.get("ltv", 40) or 40)
        icr = float(row.get("icr", 3.0) or 3.0)
        material = {"ltv": ltv, "icr": icr}
        score = 0.5 * (1 - _norm(ltv, 30, 60)) + 0.5 * _norm(icr, 1.0, 5.0)
    else:
        # generic
        controversies = float(row.get("controversies", 0) or 0)
        material = {"controversies": controversies}
        score = 1 - _norm(controversies, 0, 5)
    
    return SustMetrics(score=round(score,3), trajectory=traj, material=material)
