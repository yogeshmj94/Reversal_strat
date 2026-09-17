# H4 Hammer Reversal Research

Reproducible forex backtest for a bullish H4 hammer after at least two
consecutive bearish H4 candles. The same signals are evaluated independently
at fixed 2R and 3R targets, with green and red hammers reported separately.

## Frozen baseline rule

- Signal timeframe: H4 (UTC-aligned candles).
- Context: the candles immediately preceding the hammer include at least two
  consecutive bearish candles (`close < open`).
- Hammer: lower wick is at least 2x the real body, upper wick is no larger
  than the real body, and the body is no more than one-third of the full range.
- Direction: both green (`close >= open`) and red (`close < open`) hammers qualify.
- Entry: hammer close, after the H4 candle has completed.
- Stop: hammer low (no buffer in the baseline).
- Targets: entry + 2x risk and entry + 3x risk, evaluated separately.
- Execution: future M1 bid candles; if SL and TP occur in the same M1 candle,
  the conservative result is SL.
- Sample: 20 liquid forex pairs, 2023-09-15 through 2025-09-15.

The thresholds are intentionally explicit and configurable in `config.json`.
They are a testable mathematical approximation of the visual hammer in the
reference image, not a claim that every trader draws a hammer identically.

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
