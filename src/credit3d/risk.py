import math
from typing import List, Tuple

def cashflows(face: float, coupon_rate: float, freq: int, years: float):
    n = max(1, int(round(years*freq)))
    cpn = face * coupon_rate / freq
    times = [(i+1)/freq for i in range(n)]
    flows = [cpn]* (n-1) + [cpn + face]
    return times, flows

def price_from_ytm(face: float, coupon_rate: float, freq: int, ytm: float, years: float):
    times, flows = cashflows(face, coupon_rate, freq, years)
    pv = 0.0
    for t, cf in zip(times, flows):
        pv += cf / ((1 + ytm/freq)**(freq*t))
    return pv

def ytm_from_price(price: float, face: float, coupon_rate: float, freq: int, years: float, guess: float = 0.03):
    # Newton-Raphson
    y = guess
    for _ in range(100):
        p = price_from_ytm(face, coupon_rate, freq, y, years)
        # derivative dp/dy
        times, flows = cashflows(face, coupon_rate, freq, years)
        dp = 0.0
        for t, cf in zip(times, flows):
            df = (1 + y/freq)**(freq*t)
            dp -= (cf * (t)) / ((1 + y/freq)) * (1/df)
        # Scale derivative because of discrete compounding
        dp = dp
        err = p - price
        if abs(err) < 1e-8:
            break
        if dp == 0:
            break
        y -= err/dp
        if y < -0.99: y = -0.99
    return max(y, -0.99)

def modified_duration(price: float, face: float, coupon_rate: float, freq: int, ytm: float, years: float):
    bump = 1e-4  # 1bp in decimal terms for yield
    p_up = price_from_ytm(face, coupon_rate, freq, ytm + bump, years)
    p_dn = price_from_ytm(face, coupon_rate, freq, ytm - bump, years)
    # Dollar duration ~ (p_dn - p_up)/2
    dd = (p_dn - p_up)/2.0
    mod_dur = dd / (price * bump)
    return abs(mod_dur)

def dv01(price: float, mod_duration: float):
    # DV01 per 100 face for 1bp move (price measured per 100 notional)
    return mod_duration * price * 1e-4

def liquidity_bucket(issue_size_mil: float):
    # simple 1-5 scale
    if issue_size_mil >= 1000: return 5
    if issue_size_mil >= 500: return 4
    if issue_size_mil >= 250: return 3
    if issue_size_mil >= 100: return 2
    return 1

def key_rate_weights(tenor_years: float, nodes = (1,3,5,7,10)) -> dict:
    # Triangular weights based on distance to nodes, normalized
    dists = []
    for n in nodes:
        d = abs(tenor_years - n) + 1e-9
        dists.append(1.0/d)
    s = sum(dists)
    return {n: w/s for n, w in zip(nodes, dists)}

def krd_vector(dv01_value: float, tenor_years: float, nodes = (1,3,5,7,10)) -> dict:
    w = key_rate_weights(tenor_years, nodes)
    return {n: dv01_value * w[n] for n in nodes}

def shock_pl(price: float, dv01_value: float, shock_bps: float):
    # Approximate price P/L for spread shock in bps
    return -dv01_value * shock_bps
