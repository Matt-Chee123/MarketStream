import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


WITH_RING_CSV    = Path("../data/latenciesBuffer.csv")
WITHOUT_RING_CSV = Path("../data/latencies.csv")
OUTPUT_PLOT      = Path("../data/latency_comparison.png")

REQUIRED = {"t_binance_ms", "t_received_ns", "t_sent_ns"}


def load(path: Path, label: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        sys.exit(f"{path}: missing columns {missing}")
    if df.empty:
        sys.exit(f"{path}: no rows")
    df = df.sort_values("t_received_ns").reset_index(drop=True)
    df["handoff_us"] = (df["t_sent_ns"] - df["t_received_ns"]) / 1_000.0
    df["e2e_ms"] = df["t_sent_ns"] / 1e6 - df["t_binance_ms"]
    df["variant"] = label
    return df


def pcts(s: pd.Series) -> dict:
    return {
        "n": len(s),
        "mean": s.mean(),
        "p50": s.quantile(0.50),
        "p95": s.quantile(0.95),
        "p99": s.quantile(0.99),
        "p999": s.quantile(0.999),
        "max": s.max(),
    }


def throughput(df: pd.DataFrame) -> float:
    span_s = (df["t_received_ns"].max() - df["t_received_ns"].min()) / 1e9
    return len(df) / span_s if span_s > 0 else float("nan")


def fmt_row(name: str, st: dict, unit: str) -> str:
    return (f"  {name:11s} n={st['n']:>7d}  "
            f"mean={st['mean']:8.2f}  "
            f"p50={st['p50']:8.2f}  "
            f"p95={st['p95']:8.2f}  "
            f"p99={st['p99']:8.2f}  "
            f"p999={st['p999']:9.2f}  "
            f"max={st['max']:9.2f}  [{unit}]")


def report(df: pd.DataFrame, label: str) -> None:
    span_s = (df["t_received_ns"].max() - df["t_received_ns"].min()) / 1e9
    print(f"\n=== {label} ===")
    print(f"  rows:       {len(df):,}")
    print(f"  duration:   {span_s:.2f} s")
    print(f"  throughput: {throughput(df):,.0f} events/s")
    print(fmt_row("handoff", pcts(df["handoff_us"]), "us"))
    print(fmt_row("end-to-end", pcts(df["e2e_ms"]), "ms"))


def plot_cdf(ax, series: pd.Series, label: str) -> None:
    x = np.sort(series.values)
    y = np.arange(1, len(x) + 1) / len(x)
    ax.plot(x, y, label=label, linewidth=2)


def main() -> None:
    ring = load(WITH_RING_CSV, "ring")
    q = load(WITHOUT_RING_CSV, "queue")

    report(ring, "WITH ring buffer")
    report(q, "WITHOUT ring buffer (queue.Queue)")

    print("\n=== handoff speedup (queue.Queue / ring) ===")
    for p, name in [(0.50, "p50"), (0.95, "p95"), (0.99, "p99"), (0.999, "p999")]:
        a = ring["handoff_us"].quantile(p)
        b = q["handoff_us"].quantile(p)
        ratio = b / a if a > 0 else float("inf")
        print(f"  {name:5s}: {ratio:6.2f}x   ({b:9.2f} us  ->  {a:8.2f} us)")

    tr, tq = throughput(ring), throughput(q)
    print(f"\n=== throughput ===")
    print(f"  ring:  {tr:>10,.0f} events/s")
    print(f"  queue: {tq:>10,.0f} events/s")
    if tq > 0:
        print(f"  ratio: {tr / tq:>10.2f}x")

    if abs((ring["t_received_ns"].max() - ring["t_received_ns"].min())
           - (q["t_received_ns"].max() - q["t_received_ns"].min())) > 30 * 1e9:
        print("\n  [warn] runs differ in duration by >30s -- "
              "throughput comparison is sensitive to volatility")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, xlog in zip(axes, [False, True]):
        plot_cdf(ax, ring["handoff_us"], "ring buffer")
        plot_cdf(ax, q["handoff_us"], "queue.Queue")
        ax.set_xlabel("handoff latency (us)")
        ax.set_ylabel("CDF")
        ax.set_title("Reader -> Publisher handoff" + (" (log x)" if xlog else ""))
        ax.grid(True, alpha=0.3)
        if xlog:
            ax.set_xscale("log")
        for df, color in [(ring, "C0"), (q, "C1")]:
            ax.axvline(df["handoff_us"].quantile(0.99),
                       color=color, ls="--", alpha=0.5)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_PLOT, dpi=150)
    print(f"\nPlot written to {OUTPUT_PLOT.resolve()}")


if __name__ == "__main__":
    main()