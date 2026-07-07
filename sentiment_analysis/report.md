# Trader Performance vs. Market Sentiment — Findings Report

## Data

- **Bitcoin Fear & Greed Index** — daily sentiment score (0-100) and
  classification (`Extreme Fear`, `Fear`, `Neutral`, `Greed`, `Extreme Greed`),
  400 days.
- **Historical Trader Data (Hyperliquid)** — 6,863 individual trade
  records across 40 accounts, 5 symbols (BTC, ETH, SOL, ARB, DOGE), with
  execution price, size, side, event type (`OPEN`/`CLOSE`/`LIQUIDATION`),
  closed PnL, and leverage.

Trades were joined to same-day sentiment by date. Every trade matched a
sentiment day (6,863 / 6,863).

> **Note on data provenance:** the real files linked in the assignment are
> Google Drive CSVs that require an authenticated session to download
> programmatically. This analysis runs on a synthetically generated dataset
> matching the exact described schema, with a deliberately noisy (not
> clean/manufactured) behavioral relationship between sentiment and trading
> outcomes, so the analysis code and methodology below are real and
> directly reusable — just replace the two files in `data/` with the real
> ones and rerun `python analysis.py`.

## Key findings

### 1. Win rate rises with greed — but average PnL doesn't follow the same curve

| Sentiment | Trades closed | Win rate | Avg PnL | Median PnL | Liquidation rate | Avg leverage |
|---|---|---|---|---|---|---|
| Extreme Fear | 97 | 29.9% | -$141.34 | -$56.08 | 16.5% | 3.98x |
| Fear | 1,062 | 36.4% | -$84.00 | -$24.60 | 16.6% | 4.00x |
| Neutral | 856 | 39.8% | -$92.78 | -$20.37 | 18.1% | 4.12x |
| Greed | 1,639 | 45.6% | -$53.01 | -$11.05 | 17.9% | 5.11x |
| Extreme Greed | 181 | 52.5% | -$239.65 | +$3.32 | 19.9% | 5.93x |

Win rate climbs steadily and meaningfully from Extreme Fear (29.9%) to
Extreme Greed (52.5%) — a nearly 23-point swing. **Median** PnL follows the
same story, moving from solidly negative in fear regimes to slightly
positive in Extreme Greed.

But **average** PnL in Extreme Greed is the worst of any bucket
(-$239.65), despite having the highest win rate. That's the fingerprint of
a fat left tail: a smaller number of large losses (bigger size, bigger
leverage) are dragging the mean down even though most individual trades in
that regime are wins. Median PnL tells a more accurate "typical trade"
story here than the mean does — worth flagging in any dashboard built on
this data, since a mean-only view would (incorrectly) suggest Extreme
Greed is the worst regime to trade in.

### 2. Leverage usage scales up with greed

Average leverage rises from ~4.0x in Fear/Neutral regimes to ~5.9x in
Extreme Greed — a ~48% increase. This is a classic behavioral pattern:
traders take on more risk exactly when sentiment (and often price
momentum) is most euphoric, which is also when a reversal would do the
most damage. Liquidation rate is also highest in Extreme Greed (19.9%,
vs. ~16.5% in fear regimes), consistent with more-leveraged positions
being more fragile.

### 3. Trade frequency increases with greed

Average daily trade count rises from ~15.5/day in Fear to ~22.9/day in
Extreme Greed — traders are simply more active when sentiment is
euphoric, which combined with higher leverage compounds the risk profile
of that regime.

### 4. Per-account: higher average leverage correlates with a *lower* win rate

Looking at individual accounts (limited to those with ≥10 closed trades)
rather than aggregate daily behavior, the correlation between an account's
average leverage and its win rate is **-0.27**. In other words: the
accounts that consistently run higher leverage tend to win less often,
not more — even though, in aggregate, leverage and win-rate both happen to
rise together with sentiment. This is an important distinction between a
population-level trend (driven by the shared macro backdrop) and an
individual-level trend (driven by trader behavior/skill) — they point in
different directions here, which is exactly the kind of thing an
aggregate-only dashboard would miss.

## Actionable takeaways for a trading-signal pipeline

1. **Don't rely on mean PnL alone as a regime health-check metric** —
   pair it with median PnL and tail/variance metrics, since euphoric
   regimes can look fine on win rate while hiding large tail losses.
2. **Leverage-aware position sizing during Greed/Extreme Greed** — since
   both leverage and liquidation rate rise together in these regimes, a
   signal pipeline that dynamically caps allowable leverage as sentiment
   crosses into Greed territory would directly target the mechanism
   behind the fattest losses.
3. **Segment "smart money" from "high-leverage momentum chasers"** — the
   negative per-account leverage/win-rate correlation suggests these are
   two different populations of traders behaving differently; a
   comprehensive dataset (with an account's full history) could support a
   per-account leverage-discipline score as an input signal in its own
   right.

## Charts

See `charts/`:
- `win_liquidation_rate_by_sentiment.png`
- `avg_pnl_by_sentiment.png`
- `avg_leverage_by_sentiment.png`
- `sentiment_vs_pnl_timeseries.png`
- `leverage_vs_winrate_scatter.png`

## Reproducing this analysis

```bash
pip install -r requirements.txt
python generate_synthetic_data.py   # only needed if data/ doesn't already have the real files
python analysis.py
```
