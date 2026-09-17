import pandas as pd

from src.engine import find_signals, is_reversal_candle, simulate


CFG = {
    "minimum_bearish_candles": 2,
    "maximum_body_zone_of_range": 0.30,
    "maximum_close_gap_from_extreme": 0.02,
    "stop_buffer_pips": 1.0,
    "trend_lookback_h4_bars": [],
    "minimum_trend_votes": 0,
}


def candle(o, h, l, c):
    return pd.Series({"open": o, "high": h, "low": l, "close": c})


def test_bullish_red_and_green_geometry():
    assert is_reversal_candle(candle(100, 100, 90, 97), "bullish", CFG)
    assert is_reversal_candle(candle(97, 100, 90, 99.8), "bullish", CFG)
    assert not is_reversal_candle(candle(100, 100.1, 90, 97), "bullish", CFG)


def test_bearish_is_exact_mirror():
    assert is_reversal_candle(candle(90, 100, 90, 93), "bearish", CFG)
    assert is_reversal_candle(candle(93, 100, 90, 90.2), "bearish", CFG)
    assert not is_reversal_candle(candle(90, 100, 89.9, 93), "bearish", CFG)


def test_requires_immediately_consecutive_bearish_context():
    idx = pd.date_range("2025-01-01", periods=4, freq="4h", tz="UTC")
    h4 = pd.DataFrame([
        (105, 106, 103, 104),
        (104, 105, 101, 102),
        (103, 103, 97, 102.9),
        (103, 104, 102, 103.5),
    ], columns=["open", "high", "low", "close"], index=idx)
    signals = find_signals("EURUSD", h4, CFG)
    assert len(signals) == 1
    assert signals[0].preceding_bearish_count == 2
    assert signals[0].entry_time == idx[2] + pd.Timedelta(hours=4)
    assert signals[0].hammer_color == "red"
    assert signals[0].setup_direction == "bullish"


def test_simulation_never_uses_hammer_candle_and_sl_wins_tie():
    idx = pd.to_datetime(["2025-01-01T08:00Z", "2025-01-01T12:00Z"])
    h4 = pd.DataFrame([
        (105, 106, 103, 104), (104, 105, 102, 103), (103, 103, 99, 102.95)
    ], columns=["open", "high", "low", "close"], index=pd.date_range("2025-01-01", periods=3, freq="4h", tz="UTC"))
    signal = find_signals("EURUSD", h4, CFG)[0]
    m1 = pd.DataFrame({
        "timestamp": idx,
        "open": [104, 104], "high": [999, 115], "low": [0, 98], "close": [104, 104]
    })
    result = simulate(signal, m1, 2.0)
    assert result["outcome"] == "SL"
    assert result["ambiguous_bar"] is True
    assert result["exit_time"] == idx[1]


def test_majority_trend_filter_accepts_aligned_signal_and_rejects_opposite():
    idx = pd.date_range("2025-01-01", periods=6, freq="4h", tz="UTC")
    h4 = pd.DataFrame([
        (95, 96, 94, 95),
        (96, 97, 95, 96),
        (97, 98, 96, 97),
        (101, 102, 99, 100),
        (100, 101, 97, 98),
        (99, 99, 93, 98.9),
    ], columns=["open", "high", "low", "close"], index=idx)
    cfg = {**CFG, "trend_lookback_h4_bars": [3, 4, 5], "minimum_trend_votes": 2}
    signals = find_signals("EURUSD", h4, cfg)
    assert len(signals) == 1
    assert signals[0].setup_direction == "bullish"
    assert signals[0].trend_votes == 3
