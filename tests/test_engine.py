import pandas as pd

from src.engine import find_signals, is_hammer, simulate


CFG = {
    "minimum_bearish_candles": 2,
    "minimum_lower_wick_to_body": 2.0,
    "maximum_upper_wick_to_body": 1.0,
    "maximum_body_to_range": 1 / 3,
    "stop_buffer_pips": 0.0,
}


def candle(o, h, l, c):
    return pd.Series({"open": o, "high": h, "low": l, "close": c})


def test_green_and_red_hammers_qualify():
    assert is_hammer(candle(100, 101.2, 96, 101), CFG)
    assert is_hammer(candle(101, 101.2, 96, 100), CFG)


def test_short_lower_wick_does_not_qualify():
    assert not is_hammer(candle(100, 101.2, 98.5, 101), CFG)


def test_requires_immediately_consecutive_bearish_context():
    idx = pd.date_range("2025-01-01", periods=4, freq="4h", tz="UTC")
    h4 = pd.DataFrame([
        (105, 106, 103, 104),
        (104, 105, 101, 102),
        (102, 103.2, 97, 103),
        (103, 104, 102, 103.5),
    ], columns=["open", "high", "low", "close"], index=idx)
    signals = find_signals("EURUSD", h4, CFG)
    assert len(signals) == 1
    assert signals[0].preceding_bearish_count == 2
    assert signals[0].entry_time == idx[2] + pd.Timedelta(hours=4)
    assert signals[0].hammer_color == "green"


def test_simulation_never_uses_hammer_candle_and_sl_wins_tie():
    idx = pd.to_datetime(["2025-01-01T08:00Z", "2025-01-01T12:00Z"])
    h4 = pd.DataFrame([
        (105, 106, 103, 104), (104, 105, 102, 103), (103, 104, 99, 104)
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
