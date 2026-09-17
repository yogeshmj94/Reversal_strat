from __future__ import annotations


def _table(entries: dict) -> list[str]:
    lines = ["| Cohort | Trades | Wins | Losses | Win rate | Net R | Expectancy | PF |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for name, m in entries.items():
        lines.append(f"| {name} | {m['closed_trades']} | {m['wins']} | {m['losses']} | {m['win_rate_pct']:.2f}% | {m['net_r']:.2f} | {m['expectancy_r']:.3f}R | {m['profit_factor']} |")
    return lines


def render(summary: dict, cfg: dict) -> str:
    cohorts = summary["by_color_and_target"]
    lines = [
        "# H4 Hammer Reversal — Baseline Results", "",
        f"Sample: {cfg['date_from']} to {cfg['date_to']}, {len(cfg['pairs'])} forex pairs. Entry at hammer close; stop at hammer low; future M1 execution.", "",
        "## Primary comparison", "", *_table(cohorts), "",
        "Break-even win rates before spread, slippage, and commission are 33.33% at 2R and 25.00% at 3R.", "",
        "## Reading the result", "",
        "Compare expectancy and sample size, not win rate alone. A color is a candidate for exclusion only if its out-of-sample expectancy remains inferior after costs; this baseline is hypothesis generation, not proof of a durable edge.", "",
        "## Important limitations", "",
        "- Results use bid OHLC and do not yet deduct spread, slippage, commission, or swap.",
        "- Hammer recognition is a numeric approximation of a visual pattern.",
        "- Entry is modeled at the exact H4 close; live fills can be worse around the boundary.",
        "- SL wins ties when both SL and TP appear inside one M1 bar.",
        "- Signals may overlap; the report is signal-level, not a constrained portfolio simulation.",
        "- The same sample was used to compare variants, so any chosen rule needs out-of-sample validation.", "",
        "## Next validation", "",
        "Freeze the preferred color/target, add realistic pair-specific costs, then test a later untouched period. Do not optimize hammer ratios until the baseline result is recorded.", "",
    ]
    return "\n".join(lines)
