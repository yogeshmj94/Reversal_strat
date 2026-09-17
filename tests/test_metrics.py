import pandas as pd

from src.metrics import summarize


def test_summary_math():
    rows = pd.DataFrame({
        "outcome": ["TP", "SL", "OPEN"],
        "realized_r": [2.0, -1.0, 0.0],
        "ambiguous_bar": [False, True, False],
    })
    result = summarize(rows)
    assert result["closed_trades"] == 2
    assert result["win_rate_pct"] == 50.0
    assert result["net_r"] == 1.0
    assert result["expectancy_r"] == 0.5
    assert result["profit_factor"] == 2.0
