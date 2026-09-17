# Methodology and decision log

## Research question

After at least two immediately consecutive bearish H4 candles, does a bullish
hammer reversal have positive expectancy when entered at its close with the
hammer low as stop? Do green and red hammers behave differently, and is 2R or
3R the better fixed target?

## Why the hammer is quantified this way

The reference image conveys a small body near the candle high and a long lower
tail. For reproducibility, the baseline requires:

1. lower wick >= 2 real bodies;
2. upper wick <= 1 real body; and
3. real body <= one-third of the full high-low range.

Both red and green bodies qualify. A zero-body doji is excluded because it
cannot be assigned to the requested red/green comparison and wick/body ratios
would be undefined.

## Timeline and look-ahead control

The hammer called `Live-1` is fully closed before entry. For a hammer beginning
at 08:00 UTC, its close and modeled entry time are 12:00 UTC. Only M1 candles
at or after 12:00 are inspected for exits. The hammer's own high/low can never
trigger its stop or target retroactively.

## Exit accounting

The same unique signal is duplicated into independent 2R and 3R trials. This
answers the target comparison cleanly; it does not imply taking both positions.
If one M1 candle spans both levels, OHLC cannot reveal order, so the test assigns
SL. Trades unresolved at the dataset boundary are marked OPEN and excluded from
win rate and expectancy but counted in the report.

## Current scope

This first pass is a raw signal study. It includes no session filter, trend
filter, spread, slippage, commission, swap, position-sizing constraint, or cap
on simultaneous trades. Those belong in robustness and portfolio tests after
the baseline is observed.
