from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd


PIP_SIZE = {"JPY": 0.01}


def pip_size(symbol: str) -> float:
    return PIP_SIZE["JPY"] if symbol.endswith("JPY") else 0.0001


def to_h4(m1: pd.DataFrame) -> pd.DataFrame:
    """Build completed, UTC-aligned H4 OHLC bars from sorted M1 data."""
    frame = m1.set_index("timestamp")
    h4 = frame.resample("4h", label="left", closed="left").agg(
        open=("open", "first"),
        high=("high", "max"),
        low=("low", "min"),
        close=("close", "last"),
        minute_count=("close", "count"),
    )
    return h4.dropna(subset=["open", "high", "low", "close"])


@dataclass(frozen=True)
class Signal:
    symbol: str
    hammer_start: pd.Timestamp
    entry_time: pd.Timestamp
    hammer_color: str
    preceding_bearish_count: int
    open: float
    high: float
    low: float
    close: float
    body: float
    lower_wick: float
    upper_wick: float
    range: float
    entry: float
    stop: float
    risk: float

    def row(self) -> dict:
        return asdict(self)


def is_hammer(row: pd.Series, cfg: dict) -> bool:
    candle_range = float(row.high - row.low)
    if candle_range <= 0:
        return False
    body = abs(float(row.close - row.open))
    # A zero-body doji has undefined wick/body ratios and is not classified as
    # red or green for this experiment.
    if body <= 0:
        return False
    lower_wick = float(min(row.open, row.close) - row.low)
    upper_wick = float(row.high - max(row.open, row.close))
    return (
        lower_wick >= cfg["minimum_lower_wick_to_body"] * body
        and upper_wick <= cfg["maximum_upper_wick_to_body"] * body
        and body / candle_range <= cfg["maximum_body_to_range"]
    )


def find_signals(symbol: str, h4: pd.DataFrame, cfg: dict) -> list[Signal]:
    signals: list[Signal] = []
    minimum = int(cfg["minimum_bearish_candles"])
    buffer = float(cfg["stop_buffer_pips"]) * pip_size(symbol)
    for i in range(minimum, len(h4)):
        hammer = h4.iloc[i]
        if not is_hammer(hammer, cfg):
            continue
        bearish_count = 0
        j = i - 1
        while j >= 0 and h4.iloc[j].close < h4.iloc[j].open:
            bearish_count += 1
            j -= 1
        if bearish_count < minimum:
            continue
        entry = float(hammer.close)
        stop = float(hammer.low) - buffer
        risk = entry - stop
        if risk <= 0:
            continue
        start = h4.index[i]
        signals.append(
            Signal(
                symbol=symbol,
                hammer_start=start,
                entry_time=start + pd.Timedelta(hours=4),
                hammer_color="green" if hammer.close >= hammer.open else "red",
                preceding_bearish_count=bearish_count,
                open=float(hammer.open), high=float(hammer.high),
                low=float(hammer.low), close=float(hammer.close),
                body=abs(float(hammer.close - hammer.open)),
                lower_wick=float(min(hammer.open, hammer.close) - hammer.low),
                upper_wick=float(hammer.high - max(hammer.open, hammer.close)),
                range=float(hammer.high - hammer.low),
                entry=entry, stop=stop, risk=risk,
            )
        )
    return signals


def simulate(signal: Signal, m1: pd.DataFrame, target_r: float) -> dict:
    """Resolve one signal on future M1 bars with conservative ambiguous bars."""
    target = signal.entry + target_r * signal.risk
    # searchsorted avoids building a million-row boolean mask for every signal.
    start = int(m1["timestamp"].searchsorted(signal.entry_time, side="left"))
    future = m1.iloc[start:]
    for bar in future.itertuples(index=False):
        sl_hit = float(bar.low) <= signal.stop
        tp_hit = float(bar.high) >= target
        if sl_hit:
            return {
                "target_r": target_r, "target": target, "outcome": "SL",
                "realized_r": -1.0, "exit_time": bar.timestamp,
                "ambiguous_bar": bool(tp_hit),
            }
        if tp_hit:
            return {
                "target_r": target_r, "target": target, "outcome": "TP",
                "realized_r": target_r, "exit_time": bar.timestamp,
                "ambiguous_bar": False,
            }
    return {
        "target_r": target_r, "target": target, "outcome": "OPEN",
        "realized_r": 0.0, "exit_time": pd.NaT, "ambiguous_bar": False,
    }
