# Methodology and decision log

## Current v3 research question

Do the user-defined bullish and mirrored bearish reversal candles have positive
expectancy after at least two opposite-colour H4 context candles? How do signal
direction, candle colour, and fixed 2R versus 3R targets compare?

V3 additionally requires H4 time-series momentum to agree with the proposed
trade. Returns over 180, 540 and 1,080 completed H4 bars approximate one, three
and six trading months. At least two lookbacks must be positive for a bullish
entry or negative for a bearish entry. The periods and voting threshold are
frozen before inspecting results.

## Signal geometry

All percentages use the signal candle's high-low range.

For a bullish red candle, open must equal high and close must be within the top
30% of the range. For a bullish green candle, open must be within the top 30%
and close within the top 2%. The bearish definitions are exact vertical mirrors.

A zero-body doji is excluded because it cannot be assigned to the requested
red/green comparison. Stops are one pip beyond the signal extreme.

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
