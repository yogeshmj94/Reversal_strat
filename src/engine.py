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
    setup_direction: str
    trend_votes: int
    trend_lookback_returns: str
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


def is_reversal_candle(row: pd.Series, direction: str, cfg: dict) -> bool:
    """Apply the user-defined, range-normalized hammer/shooting-star geometry."""
    candle_range = float(row.high - row.low)
    if candle_range <= 0 or row.close == row.open:
        return False
    zone = cfg["maximum_body_zone_of_range"] * candle_range
    close_gap = cfg["maximum_close_gap_from_extreme"] * candle_range
    eps = max(candle_range * 1e-9, 1e-12)
    green = row.close > row.open
    if direction == "bullish":
        if green:
            return row.high - row.open <= zone + eps and row.high - row.close <= close_gap + eps
        return abs(row.high - row.open) <= eps and row.high - row.close <= zone + eps
    if direction == "bearish":
        if green:
            return abs(row.open - row.low) <= eps and row.close - row.low <= zone + eps
        return row.open - row.low <= zone + eps and row.close - row.low <= close_gap + eps
    raise ValueError(f"Unknown direction: {direction}")


def is_hammer(row: pd.Series, cfg: dict) -> bool:
    """Backward-compatible alias for the bullish pattern."""
    return is_reversal_candle(row, "bullish", cfg)


def find_signals(symbol: str, h4: pd.DataFrame, cfg: dict) -> list[Signal]:
    signals: list[Signal] = []
    minimum = int(cfg["minimum_bearish_candles"])
    trend_lookbacks = [int(x) for x in cfg.get("trend_lookback_h4_bars", [])]
    minimum_votes = int(cfg.get("minimum_trend_votes", 0))
    longest_lookback = max(trend_lookbacks, default=0)
    buffer = float(cfg["stop_buffer_pips"]) * pip_size(symbol)
    for i in range(max(minimum, longest_lookback), len(h4)):
      hammer = h4.iloc[i]
      for direction in ("bullish", "bearish"):
        if not is_reversal_candle(hammer, direction, cfg):
            continue
        context_count = 0
        j = i - 1
        while j >= 0:
            prior = h4.iloc[j]
            required = prior.close < prior.open if direction == "bullish" else prior.close > prior.open
            if not required:
                break
            context_count += 1
            j -= 1
        if context_count < minimum:
            continue
        returns = [float(hammer.close / h4.iloc[i - lookback].close - 1.0) for lookback in trend_lookbacks]
        votes = sum(r > 0 for r in returns) if direction == "bullish" else sum(r < 0 for r in returns)
        if votes < minimum_votes:
            continue
        entry = float(hammer.close)
        stop = float(hammer.low) - buffer if direction == "bullish" else float(hammer.high) + buffer
        risk = abs(entry - stop)
        if risk <= 0:
            continue
        start = h4.index[i]
        signals.append(
            Signal(
                symbol=symbol, setup_direction=direction, trend_votes=votes,
                trend_lookback_returns="|".join(f"{r:.8f}" for r in returns),
                hammer_start=start,
                entry_time=start + pd.Timedelta(hours=4),
                hammer_color="green" if hammer.close >= hammer.open else "red",
                preceding_bearish_count=context_count,
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
    target = signal.entry + target_r * signal.risk if signal.setup_direction == "bullish" else signal.entry - target_r * signal.risk
    # searchsorted avoids building a million-row boolean mask for every signal.
    start = int(m1["timestamp"].searchsorted(signal.entry_time, side="left"))
    future = m1.iloc[start:]
    for bar in future.itertuples(index=False):
        if signal.setup_direction == "bullish":
            sl_hit = float(bar.low) <= signal.stop
            tp_hit = float(bar.high) >= target
        else:
            sl_hit = float(bar.high) >= signal.stop
            tp_hit = float(bar.low) <= target
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
