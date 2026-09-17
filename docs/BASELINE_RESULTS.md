# H4 hammer reversal baseline results

Workflow: [run 35230897224](https://github.com/yogeshmj94/Reversal_strat/actions/runs/35230897224)  
Sample: 2023-09-15 to 2025-09-15, 20 forex pairs  
Signals: 793 unique H4 hammers (409 green, 384 red)

## Primary results

| Hammer | Target | Trades | Wins | Win rate | Break-even | Net R | Expectancy | Profit factor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Green | 2R | 409 | 137 | 33.50% | 33.33% | +2R | +0.0049R | 1.007 |
| Green | 3R | 409 | 100 | 24.45% | 25.00% | -9R | -0.0220R | 0.971 |
| Red | 2R | 384 | 127 | 33.07% | 33.33% | -3R | -0.0078R | 0.988 |
| Red | 3R | 384 | 101 | 26.30% | 25.00% | +20R | +0.0521R | 1.071 |

All signals combined returned -1R at 2R and +11R at 3R. These figures are
before spread, slippage, commission, and swap.

## Decision

Do not choose green-only, red-only, 2R, or 3R for production from this test.
The baseline is effectively break-even before costs and therefore negative
after realistic execution expenses. Red 3R is the best candidate for further
research, not a tradeable conclusion.

There is no reliable evidence that red and green hammers perform differently:

- At 2R, red minus green win rate was -0.42 percentage points. The approximate
  95% confidence interval was -6.99 to +6.14 points.
- At 3R, red minus green win rate was +1.85 points. The approximate 95%
  confidence interval was -4.21 to +7.91 points.

Every primary cohort's 95% win-rate interval includes its break-even rate.
Red 3R's 26.30% win rate had a 95% interval of 22.15%-30.92%; its advantage
over the 25% break-even rate was not statistically significant (p=0.56).

## Stability checks

The sample was split at 2024-09-15:

| Hammer | Target | First year | Second year |
|---|---:|---:|---:|
| Green | 2R | +37R | -35R |
| Green | 3R | +5R | -14R |
| Red | 2R | -3R | 0R |
| Red | 3R | +6R | +14R |

Green 2R reversed sharply between years, showing regime instability. Red 3R
was positive in both halves, but the total edge remained too small to absorb
normal trading costs with confidence.

The signal-level chronological maximum drawdowns were 52R for green 2R, 42R
for green 3R, 19R for red 2R, and 20R for red 3R. These are not portfolio
drawdowns because signals can overlap across pairs.

Pair samples were small (typically 11-35 trades per colour), and results were
widely dispersed. Examples include red 3R at +11R on AUDCAD and NZDUSD but
-11R on USDCHF and -9R on EURNZD. This is not enough evidence to add or remove
individual pairs.

## Exploratory finding: bearish-candle count

This was not one of the frozen primary comparisons and must not be treated as
confirmed evidence.

| Preceding bearish candles | Hammer | Target | Trades | Net R | Expectancy |
|---:|---|---:|---:|---:|---:|
| Exactly 3 | Red | 3R | 101 | +35R | +0.347R |
| Exactly 3 | Red | 2R | 101 | +13R | +0.129R |
| 4 or more | Green | 3R | 87 | +21R | +0.241R |
| 4 or more | Green | 2R | 87 | +18R | +0.207R |

Red 3R after exactly three bearish candles was positive in both time halves:
+8R from 64 trades in the first year and +27R from 37 trades in the second.
Because this rule was discovered after inspecting the same dataset, its result
is subject to selection bias. It should be frozen as a new hypothesis and
tested on a later untouched period with execution costs included.

## Execution and modeling limitations

- Dukascopy bid OHLC was used; spread, slippage, commission, and swap were not.
- Entry was modeled at the exact H4 close.
- The stop had no buffer below the hammer low.
- If SL and TP occurred inside the same M1 candle, SL won the tie. This affected
  only one red-hammer trade.
- Signals could overlap. No capital, correlation, or simultaneous-position cap
  was applied.
- Hammer detection is a deterministic approximation of a visual pattern.

## Recommended next test

Freeze one new hypothesis: red hammer, exactly three immediately preceding
bearish H4 candles, entry at hammer close, stop at hammer low, and 3R target.
Test it on untouched data after 2025-09-15 with realistic spread and commission.
Keep the current baseline unchanged as the research control.
