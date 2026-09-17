# Bullish and bearish reversal v2 results

Workflow: [run 35241596547](https://github.com/yogeshmj94/Reversal_strat/actions/runs/35241596547)  
Sample: 2023-09-15 to 2025-09-15, 20 forex pairs  
Signals: 72 unique setups (39 bullish, 33 bearish)

## Primary results

| Direction | Candle colour | Target | Trades | Wins | Win rate | Net R | Expectancy | Profit factor |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Bullish | Green | 2R | 29 | 7 | 24.14% | -8R | -0.276R | 0.636 |
| Bullish | Green | 3R | 29 | 6 | 20.69% | -5R | -0.172R | 0.783 |
| Bullish | Red | 2R | 10 | 3 | 30.00% | -1R | -0.100R | 0.857 |
| Bullish | Red | 3R | 10 | 2 | 20.00% | -2R | -0.200R | 0.750 |
| Bearish | Green | 2R | 9 | 4 | 44.44% | +3R | +0.333R | 1.600 |
| Bearish | Green | 3R | 9 | 2 | 22.22% | -1R | -0.111R | 0.857 |
| Bearish | Red | 2R | 24 | 7 | 29.17% | -3R | -0.125R | 0.824 |
| Bearish | Red | 3R | 24 | 7 | 29.17% | +4R | +0.167R | 1.235 |

Across all signals, 2R returned -9R (-0.125R per trade) and 3R returned
-4R (-0.056R per trade). Results exclude spread, slippage, commission, and
swap, so the combined strategy is negative before execution costs.

## Direction comparison

| Direction | Target | Trades | Net R | Expectancy |
|---|---:|---:|---:|---:|
| Bullish | 2R | 39 | -9R | -0.231R |
| Bullish | 3R | 39 | -7R | -0.179R |
| Bearish | 2R | 33 | 0R | 0.000R |
| Bearish | 3R | 33 | +3R | +0.091R |

Bearish setups outperformed bullish setups in this sample. The sample is too
small to conclude that the asymmetry is durable.

## Statistical uncertainty

Every colour-and-direction cohort has a wide 95% win-rate interval:

- Bullish green: 12.2%-42.1% at 2R and 9.8%-38.4% at 3R.
- Bullish red: 10.8%-60.3% at 2R and 5.7%-51.0% at 3R.
- Bearish green: 18.9%-73.3% at 2R and 6.3%-54.7% at 3R.
- Bearish red: 14.9%-49.2% at both targets.

Each interval includes the applicable break-even win rate: 33.33% for 2R and
25% for 3R. None of the apparent winners is statistically reliable.

## Time-split stability

| Direction and colour | Target | First year | Second year |
|---|---:|---:|---:|
| Bullish green | 2R | -9R | +1R |
| Bullish green | 3R | -11R | +6R |
| Bullish red | 2R | +2R | -3R |
| Bullish red | 3R | +1R | -3R |
| Bearish green | 2R | +4R | -1R |
| Bearish green | 3R | +2R | -3R |
| Bearish red | 2R | -3R | 0R |
| Bearish red | 3R | 0R | +4R |

No colour-and-direction cohort was positive in both halves. Bearish red 3R was
flat in the first half and positive in the second, making it the least unstable
candidate, but it still had only 24 total trades.

## Frequency and definition effect

The exact extreme requirements generated only 72 setups in approximately two
years across 20 pairs, about 1.8 unique setups per month across the entire
universe. The rarest cohort, bearish green, contained only nine signals.

Exact `open = high` and `open = low` depend on feed precision. A candle that
misses equality by one tick is excluded even when it looks identical visually.
The close-within-2%-of-range rule further reduces frequency. This is faithful
to the frozen definition but makes inference and live portability difficult.

## Pair and context observations

Pair-level samples were only one to seven signals per direction. Pair winners
and losers cannot be distinguished from noise. No pair should be added or
removed based on this run.

The number of preceding context candles also produced very small subgroups.
For example, bullish setups after exactly three bearish candles returned +5R
at both targets, but this came from only seven signals and is not actionable.

## Drawdown and holding time

Signal-level maximum drawdowns ranged from 2R to 12R by cohort. Bullish green
had the largest drawdowns: 12R at 2R and 10R at 3R. Median holding times ranged
from about 9 to 23 hours. These are not portfolio drawdowns because signals may
overlap across pairs.

## Decision

Do not trade this version in production. It is negative overall before costs,
and the profitable subgroups are too small and unstable.

If the intended definition is visual rather than tick-exact, the next useful
test is a predeclared tolerance such as open within one pip of the high/low,
while leaving the 30% and 2% candle-range rules unchanged. That would test the
same visual idea with more signals and less dependence on data-feed rounding.
