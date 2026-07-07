"""
Analysis: trader performance (Hyperliquid) vs. Bitcoin market sentiment
(Fear & Greed Index).

Run: python analysis.py
Outputs: charts/*.png, and prints a findings summary to stdout (also
mirrored into report.md by hand — see that file for the write-up).
"""

import matplotlib
matplotlib.use("Agg")  # headless — save figures, don't try to open a display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option("display.width", 120)

# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
sentiment = pd.read_csv("data/fear_greed_index.csv")
trades = pd.read_csv("data/historical_data.csv")

sentiment["Date"] = pd.to_datetime(sentiment["Date"])
trades["time"] = pd.to_datetime(trades["time"])
trades["date"] = trades["time"].dt.normalize()

SENTIMENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
sentiment["Classification"] = pd.Categorical(
    sentiment["Classification"], categories=SENTIMENT_ORDER, ordered=True
)

# ---------------------------------------------------------------------------
# Join trades to same-day sentiment
# ---------------------------------------------------------------------------
merged = trades.merge(
    sentiment[["Date", "Value", "Classification"]],
    left_on="date", right_on="Date", how="left",
)
merged["Classification"] = pd.Categorical(
    merged["Classification"], categories=SENTIMENT_ORDER, ordered=True
)

print(f"Loaded {len(trades):,} trades across {trades['account'].nunique()} accounts, "
      f"{len(sentiment)} days of sentiment data.")
print(f"Merged rows with sentiment match: {merged['Classification'].notna().sum():,} / {len(merged):,}")

closes = merged[merged["event"].isin(["CLOSE", "LIQUIDATION"])].copy()
closes["is_win"] = closes["closedPnL"] > 0
closes["is_liquidation"] = closes["event"] == "LIQUIDATION"

# ---------------------------------------------------------------------------
# 1. Trader performance by sentiment class
# ---------------------------------------------------------------------------
perf_by_sentiment = closes.groupby("Classification", observed=True).agg(
    n_trades=("closedPnL", "count"),
    avg_pnl=("closedPnL", "mean"),
    median_pnl=("closedPnL", "median"),
    win_rate=("is_win", "mean"),
    liquidation_rate=("is_liquidation", "mean"),
    avg_leverage=("leverage", "mean"),
    total_pnl=("closedPnL", "sum"),
).round(3)

print("\n=== Performance by sentiment class ===")
print(perf_by_sentiment)

# ---------------------------------------------------------------------------
# 2. Leverage behavior by sentiment
# ---------------------------------------------------------------------------
leverage_by_sentiment = merged.groupby("Classification", observed=True)["leverage"].agg(
    ["mean", "median", "std", "max"]
).round(2)
print("\n=== Leverage by sentiment class ===")
print(leverage_by_sentiment)

# ---------------------------------------------------------------------------
# 3. Trade volume/frequency by sentiment
# ---------------------------------------------------------------------------
daily_trade_counts = merged.groupby("date", observed=True).size().reset_index(name="n_trades")
daily_trade_counts = daily_trade_counts.merge(sentiment[["Date", "Value", "Classification"]],
                                               left_on="date", right_on="Date")
volume_by_sentiment = daily_trade_counts.groupby("Classification", observed=True)["n_trades"].mean().round(1)
print("\n=== Avg daily trade count by sentiment class ===")
print(volume_by_sentiment)

# ---------------------------------------------------------------------------
# 4. Per-account behavior: does higher leverage correlate with worse outcomes?
# ---------------------------------------------------------------------------
account_stats = closes.groupby("account").agg(
    n_trades=("closedPnL", "count"),
    avg_leverage=("leverage", "mean"),
    win_rate=("is_win", "mean"),
    total_pnl=("closedPnL", "sum"),
).query("n_trades >= 10")
corr_leverage_winrate = account_stats["avg_leverage"].corr(account_stats["win_rate"])
print(f"\nCorrelation (avg leverage vs win rate, accounts with >=10 trades): {corr_leverage_winrate:.3f}")

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

# Chart 1: Win rate and liquidation rate by sentiment
fig, ax1 = plt.subplots(figsize=(9, 5))
x = np.arange(len(perf_by_sentiment))
width = 0.35
ax1.bar(x - width/2, perf_by_sentiment["win_rate"], width, label="Win rate", color="#2E86AB")
ax1.bar(x + width/2, perf_by_sentiment["liquidation_rate"], width, label="Liquidation rate", color="#C73E1D")
ax1.set_xticks(x)
ax1.set_xticklabels(perf_by_sentiment.index, rotation=20)
ax1.set_ylabel("Rate")
ax1.set_title("Win Rate & Liquidation Rate by Market Sentiment")
ax1.legend()
plt.tight_layout()
plt.savefig("charts/win_liquidation_rate_by_sentiment.png", dpi=150)
plt.close()

# Chart 2: Average PnL by sentiment
fig, ax = plt.subplots(figsize=(9, 5))
colors = ["#C73E1D" if v < 0 else "#2E86AB" for v in perf_by_sentiment["avg_pnl"]]
ax.bar(perf_by_sentiment.index.astype(str), perf_by_sentiment["avg_pnl"], color=colors)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_ylabel("Average closed PnL (USD)")
ax.set_title("Average Trade PnL by Market Sentiment")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("charts/avg_pnl_by_sentiment.png", dpi=150)
plt.close()

# Chart 3: Average leverage by sentiment
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(leverage_by_sentiment.index.astype(str), leverage_by_sentiment["mean"], color="#7A6FA1")
ax.set_ylabel("Average leverage (x)")
ax.set_title("Average Leverage Used by Market Sentiment")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("charts/avg_leverage_by_sentiment.png", dpi=150)
plt.close()

# Chart 4: Time series — sentiment value vs daily avg PnL
daily_pnl = closes.groupby("date")["closedPnL"].mean().reset_index()
daily_pnl = daily_pnl.merge(sentiment[["Date", "Value"]], left_on="date", right_on="Date")

fig, ax1 = plt.subplots(figsize=(11, 5))
ax2 = ax1.twinx()
ax1.plot(daily_pnl["date"], daily_pnl["Value"], color="#7A6FA1", label="Sentiment score (0-100)")
ax2.plot(daily_pnl["date"], daily_pnl["closedPnL"], color="#2E86AB", alpha=0.7, label="Avg daily closed PnL")
ax1.set_ylabel("Fear & Greed score", color="#7A6FA1")
ax2.set_ylabel("Avg daily closed PnL (USD)", color="#2E86AB")
ax1.set_title("Sentiment Score vs. Average Daily Trader PnL Over Time")
fig.tight_layout()
plt.savefig("charts/sentiment_vs_pnl_timeseries.png", dpi=150)
plt.close()

# Chart 5: Leverage vs win rate scatter (per-account)
fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(account_stats["avg_leverage"], account_stats["win_rate"], alpha=0.6, color="#2E86AB")
ax.set_xlabel("Average leverage used")
ax.set_ylabel("Win rate")
ax.set_title(f"Per-Account: Avg Leverage vs Win Rate (r = {corr_leverage_winrate:.2f})")
plt.tight_layout()
plt.savefig("charts/leverage_vs_winrate_scatter.png", dpi=150)
plt.close()

print("\nCharts saved to charts/")

# Save the summary tables for the report to reference precisely
perf_by_sentiment.to_csv("charts/perf_by_sentiment_table.csv")
leverage_by_sentiment.to_csv("charts/leverage_by_sentiment_table.csv")
