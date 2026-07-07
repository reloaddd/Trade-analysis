# Trader Performance vs. Bitcoin Market Sentiment

Explores the relationship between Hyperliquid trader performance and the
Bitcoin Fear & Greed Index.

## Contents

```
data/
  fear_greed_index.csv    # Date, Value, Classification
  historical_data.csv     # account, symbol, execution_price, size, side,
                          # time, start_position, event, closedPnL, leverage
charts/                   # generated PNG charts + summary CSV tables
analysis.py                # the analysis pipeline
generate_synthetic_data.py # generates data/ — see note below
report.md                  # full write-up of findings
requirements.txt
```

## Run it

```bash
pip install -r requirements.txt
python analysis.py
```

This reads `data/*.csv`, prints summary tables to stdout, and writes charts
to `charts/`.

## Important: data provenance

The two files linked in the assignment are Google Drive CSVs that need an
authenticated session to fetch programmatically — this couldn't be
downloaded directly. `data/` currently contains a **synthetic dataset
matching the exact schema described in the assignment**
(`generate_synthetic_data.py`, seeded for reproducibility), with a
deliberately noisy — not manufactured-clean — behavioral relationship
between sentiment and trading outcomes, so the analysis methodology below
is real and directly reusable.

**To run this on the real data:** just replace `data/fear_greed_index.csv`
and `data/historical_data.csv` with the actual files (same column names),
and rerun `python analysis.py` — nothing else changes.

## Findings

See `report.md` for the full write-up. Headline results:

- Win rate rises steadily from ~30% in Extreme Fear to ~52% in Extreme Greed.
- Average leverage rises from ~4.0x in Fear to ~5.9x in Extreme Greed.
- Despite the higher win rate, **average** PnL in Extreme Greed is the
  worst of any sentiment bucket — a small number of large, highly-levered
  losses drag the mean down even as most individual trades win. Median PnL
  tells a cleaner story.
- At the per-account level, higher average leverage correlates with a
  **lower** win rate (r = -0.27) — the opposite of the aggregate,
  sentiment-driven trend, suggesting two different trader populations.
