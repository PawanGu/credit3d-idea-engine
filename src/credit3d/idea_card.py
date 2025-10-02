from dataclasses import asdict

def render_markdown(card) -> str:
    c = asdict(card)
    krd_str = ", ".join([f"{k}y: {v}" for k,v in c['risk']['krd'].items()])
    mat = c['sust']['material']
    mat_str = ", ".join([f"{k}={v}" for k,v in mat.items()]) if mat else "-"
    lines = [
        f"## {c['issuer']} — {c['isin']} ({c['rating']}, {c['seniority']})",
        f"**Sector:** {c['sector']} | **Tenor:** {c['tenor_years']:.1f}y | **Price:** {c['price']:.2f} | **Mandate Fit:** {c['mandate_fit']}",
        "",
        "**Risk**: ",
        f"- Mod. Duration: {c['risk']['mod_duration']} | DV01/100: {c['risk']['dv01_per_100']}",
        f"- KRD: {krd_str}",
        f"- Liquidity: {c['risk']['liquidity_bucket']} | Shock P/L: 50bps {c['risk']['shock_pl_pct_50bps']:.3%}, 100bps {c['risk']['shock_pl_pct_100bps']:.3%}",
        "",
        "**Return**:",
        f"- YTM: {c['ret']['ytm']:.4f} | OAS (bond/sector): {c['ret']['bond_oas_bps']}/{c['ret']['sector_oas_bps']} bps | Gap: {c['ret']['fair_value_gap_bps']} bps",
        f"- Carry: {c['ret']['carry_bps']} bps | Rolldown: {c['ret']['rolldown_bps']} bps | Expected ΔOAS: {c['ret']['expected_delta_oas_bps']} bps",
        f"- **Expected Return (horizon): {c['ret']['expected_return_pct']:.2%}** | Expected Loss: {c['ret']['expected_loss_pct']:.2%}",
        "",
        "**Sustainability**:",
        f"- Score: {c['sust']['score']} | Trajectory: {c['sust']['trajectory']} | Material: {mat_str}",
        "",
        "---",
        ""
    ]
    return "\n".join(lines)
