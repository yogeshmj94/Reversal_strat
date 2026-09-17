# H4 Hammer Reversal Research

Reproducible forex backtest for a bullish H4 hammer after at least two
consecutive bearish H4 candles. The same signals are evaluated independently
at fixed 2R and 3R targets, with green and red hammers reported separately.

## Current v3 rule

- Signal timeframe: H4 (UTC-aligned candles).
- Bullish context: at least two immediately consecutive bearish H4 candles.
- Bullish red signal: open equals high; close is no more than 30% of the candle
  range below the high, leaving a lower wick of at least 70%.
- Bullish green signal: open is no more than 30% of the range below the high;
  close equals the high or is no more than 2% of the range below it.
- Bearish signals mirror those definitions vertically after at least two
  immediately consecutive bullish H4 candles.
- Trend filter: approximately 1-, 3- and 6-month returns measured over 180,
  540 and 1,080 completed H4 candles. At least two of three lookbacks must agree
  with the reversal direction.
- Entry: hammer close, after the H4 candle has completed.
- Stop: one pip beyond the signal low for bullish setups and one pip beyond the
  signal high for bearish setups.
- Targets: entry + 2x risk and entry + 3x risk, evaluated separately.
- Execution: future M1 bid candles; if SL and TP occur in the same M1 candle,
  the conservative result is SL.
- Sample: 20 liquid forex pairs, 2023-09-15 through 2025-09-15.

The thresholds are intentionally explicit, range-normalized, and configurable
in `config.json`.

## Run locally

```bash
pip install -r requirements.txt
python -m src.backtest --data-dir data --out-dir results/baseline
pytest -q
```

Input files are `data/EURUSD.csv`, etc., with Dukascopy-style columns:
`timestamp,open,high,low,close,volume`. Timestamp is Unix milliseconds.

The GitHub Actions workflow downloads and caches the M1 data, runs the test,
and uploads `trades.csv`, `summary.json`, and `REPORT.md` as an artifact.

See [docs/METHODOLOGY.md](docs/METHODOLOGY.md) for assumptions and bias controls.
The completed baseline findings are in
[docs/BASELINE_RESULTS.md](docs/BASELINE_RESULTS.md).
The bullish-and-bearish v2 findings are in
[docs/V2_RESULTS.md](docs/V2_RESULTS.md).
