from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .engine import find_signals, simulate, to_h4
from .metrics import build_summary
from .report import render


def load_m1(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"timestamp", "open", "high", "low", "close"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    if pd.api.types.is_numeric_dtype(frame.timestamp):
        frame["timestamp"] = pd.to_datetime(frame.timestamp, unit="ms", utc=True)
    else:
        frame["timestamp"] = pd.to_datetime(frame.timestamp, utc=True)
    return frame.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--out-dir", default="results/baseline")
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text())
    rows: list[dict] = []
    for symbol in cfg["pairs"]:
        m1 = load_m1(Path(args.data_dir) / f"{symbol}.csv")
        signals = find_signals(symbol, to_h4(m1), cfg)
        for signal in signals:
            for target_r in cfg["targets_r"]:
                rows.append({**signal.row(), **simulate(signal, m1, float(target_r))})
        print(f"{symbol}: {len(signals)} unique signals / {len(signals) * len(cfg['targets_r'])} target trials")
    trades = pd.DataFrame(rows)
    if trades.empty:
        raise RuntimeError("No qualifying signals found")
    summary = build_summary(trades)
    summary["configuration"] = cfg
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    trades.to_csv(out / "trades.csv", index=False)
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    (out / "REPORT.md").write_text(render(summary, cfg))
    print(json.dumps(summary["by_direction_color_target"], indent=2))


if __name__ == "__main__":
    main()
