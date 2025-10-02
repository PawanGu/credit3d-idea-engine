from credit3d.risk import ytm_from_price, modified_duration, dv01

def test_dv01_monotonic():
    price = 98.0
    face = 100.0
    coupon = 0.04
    freq = 2
    years = 5.0
    ytm = ytm_from_price(price, face, coupon, freq, years)
    md = modified_duration(price, face, coupon, freq, ytm, years)
    d = dv01(price, md)
    assert d > 0
    assert md > 0
