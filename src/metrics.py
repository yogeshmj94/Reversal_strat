from __future__ import annotations

import math

import pandas as pd


def summarize(group: pd.DataFrame) -> dict:
    closed = group[group.outcome.isin(["TP", "SL"])]
    wins = int((closed.outcome == "TP").sum())
    losses = int((closed.outcome == "SL").sum())
    n = len(closed)
    gross_win = float(closed.loc[closed.realized_r > 0, "realized_r"].sum())
    gross_loss = abs(float(closed.loc[closed.realized_r < 0, "realized_r"].sum()))
    expectancy = float(closed.realized_r.mean()) if n else 0.0
    return {
        "signals": int(len(group)),
        "closed_trades": int(n),
        "open_at_data_end": int((group.outcome == "OPEN").sum()),
        "wins": wins,
        "losses": losses,
        "win_rate_pct": round(100 * wins / n, 4) if n else 0.0,
        "net_r": round(float(closed.realized_r.sum()), 4),
        "expectancy_r": round(expectancy, 6),
        "profit_factor": round(gross_win / gross_loss, 6) if gross_loss else (math.inf if gross_win else 0.0),
        "ambiguous_m1_bars_counted_as_sl": int(closed.ambiguous_bar.sum()),
    }


def build_summary(trades: pd.DataFrame) -> dict:
    result = {"overall": summarize(trades), "by_target": {}, "by_color_and_target": {}, "by_pair": {}}
    for target, group in trades.groupby("target_r"):
        result["by_target"][f"{target:g}R"] = summarize(group)
    for (color, target), group in trades.groupby(["hammer_color", "target_r"]):
        result["by_color_and_target"][f"{color}_{target:g}R"] = summarize(group)
    for (symbol, color, target), group in trades.groupby(["symbol", "hammer_color", "target_r"]):
        result["by_pair"][f"{symbol}_{color}_{target:g}R"] = summarize(group)
    return result
