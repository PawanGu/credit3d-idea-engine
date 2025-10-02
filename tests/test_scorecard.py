import pandas as pd
from credit3d.dataio import load_csvs
from credit3d.scorecard import compute_scorecard

def test_scorecard_runs(tmp_path):
    bonds, curves, kpis = load_csvs('data')
    row = bonds.merge(kpis, on=['issuer','sector']).iloc[0]
    card = compute_scorecard(row, curves, 0.02, 6, 'protection')
    assert card.isin
    assert 'risk' in card.__dict__
    assert 'ret' in card.__dict__
    assert 'sust' in card.__dict__
