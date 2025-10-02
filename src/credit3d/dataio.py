import os
import pandas as pd

def load_csvs(data_dir: str):
    bonds = pd.read_csv(os.path.join(data_dir, "bonds.csv"))
    curves = pd.read_csv(os.path.join(data_dir, "curves.csv"))
    kpis = pd.read_csv(os.path.join(data_dir, "kpi_issuers.csv"))
    # Basic parsing
    bonds['maturity_yyyy_mm_dd'] = pd.to_datetime(bonds['maturity_yyyy_mm_dd'])
    bonds['tenor_years'] = ((bonds['maturity_yyyy_mm_dd'] - pd.Timestamp.today())/pd.Timedelta(days=365)).clip(lower=0.25).astype(float)
    return bonds, curves, kpis
