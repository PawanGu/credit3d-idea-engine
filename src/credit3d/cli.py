import argparse, os, datetime
import pandas as pd

from .dataio import load_csvs
from .scorecard import compute_scorecard
from .idea_card import render_markdown

def main():
    p = argparse.ArgumentParser(description="3D Credit Idea Engine (Euro IG Financials)")
    p.add_argument('--data_dir', type=str, required=True)
    p.add_argument('--horizon_months', type=int, default=6)
    p.add_argument('--funding_rate', type=float, default=0.02, help='decimal, e.g. 0.02 for 2%')
    p.add_argument('--mandate', type=str, default='protection', choices=['protection','global'])
    args = p.parse_args()
    
    bonds, curves, kpis = load_csvs(args.data_dir)
    df = bonds.merge(kpis, on=['issuer','sector'], how='left')
    
    cards = []
    for _, row in df.iterrows():
        card = compute_scorecard(row, curves, args.funding_rate, args.horizon_months, args.mandate)
        # Filter: if mandate is protection, only keep those tagged Protection
        if args.mandate == 'protection' and card.mandate_fit != 'Protection':
            continue
        cards.append(card)
    
    if not cards:
        print("No ideas matched the selected mandate/filters.")
        return
    
    ts = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    outpath = os.path.join(os.path.dirname(__file__), '..', '..', 'reports', f'ideas_{ts}.md')
    outpath = os.path.abspath(outpath)
    
    with open(outpath, 'w') as f:
        f.write(f"# 3D Credit Idea Engine — {args.mandate.title()} (h={args.horizon_months}m, funding={args.funding_rate*100:.1f}%)\n\n")
        for c in cards:
            f.write(render_markdown(c))
    
    print(f"Wrote {len(cards)} idea cards to: {outpath}")

if __name__ == '__main__':
    main()
