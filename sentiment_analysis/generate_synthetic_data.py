
import numpy as np
import pandas as pd

np.random.seed(42)

# ---------------------------------------------------------------------------
# 1. Bitcoin Fear & Greed Index
# ---------------------------------------------------------------------------
n_days = 400
dates = pd.date_range("2024-01-01", periods=n_days, freq="D")

score = 50.0
scores = []
for _ in range(n_days):
    score += np.random.normal(0, 4) + (50 - score) * 0.03  # mean reversion
    score = np.clip(score, 5, 95)
    scores.append(score)

def classify(s):
    if s < 25:
        return "Extreme Fear"
    elif s < 45:
        return "Fear"
    elif s < 55:
        return "Neutral"
    elif s < 75:
        return "Greed"
    else:
        return "Extreme Greed"

sentiment_df = pd.DataFrame({
    "Date": dates.strftime("%Y-%m-%d"),
    "Value": np.round(scores, 0).astype(int),
    "Classification": [classify(s) for s in scores],
})
sentiment_df.to_csv("data/fear_greed_index.csv", index=False)
print(f"Wrote {len(sentiment_df)} rows to data/fear_greed_index.csv")
print(sentiment_df["Classification"].value_counts())

# ---------------------------------------------------------------------------
# 2. Historical Trader Data (Hyperliquid-style)
# ---------------------------------------------------------------------------
accounts = [f"0x{i:040x}" for i in range(1, 41)]  # 40 synthetic wallet addresses
symbols = ["BTC", "ETH", "SOL", "ARB", "DOGE"]
sides = ["BUY", "SELL"]
events = ["OPEN", "CLOSE", "LIQUIDATION"]

# Map each date to its sentiment score/class so trades can be sentiment-aware
sentiment_lookup = dict(zip(sentiment_df["Date"], zip(scores, sentiment_df["Classification"])))

rows = []
trade_id = 0
for date in dates:
    date_str = date.strftime("%Y-%m-%d")
    day_score, day_class = sentiment_lookup[date_str]

    
    n_trades_today = int(np.random.poisson(lam=15 + max(0, (day_score - 50) * 0.3)))

    for _ in range(n_trades_today):
        trade_id += 1
        account = np.random.choice(accounts)
        symbol = np.random.choice(symbols)
        side = np.random.choice(sides)
        event = np.random.choice(events, p=[0.45, 0.45, 0.10])

        base_price = {"BTC": 45000, "ETH": 2400, "SOL": 100, "ARB": 1.2, "DOGE": 0.08}[symbol]
        execution_price = round(base_price * (1 + np.random.normal(0, 0.02)), 4)
        size = round(abs(np.random.lognormal(mean=0.5, sigma=1.2)), 4)

        
        leverage_bias = 3 + max(0, (day_score - 50) * 0.08)
        leverage = int(np.clip(np.random.poisson(lam=leverage_bias) + 1, 1, 50))

       
        pnl_bias = 0
        if day_class == "Extreme Greed":
            pnl_bias = 15
        elif day_class == "Greed":
            pnl_bias = 6
        elif day_class == "Fear":
            pnl_bias = -6
        elif day_class == "Extreme Fear":
            pnl_bias = -18

        closed_pnl = 0.0
        if event in ("CLOSE", "LIQUIDATION"):
            noise = np.random.normal(pnl_bias, 80)
            if event == "LIQUIDATION":
                noise = -abs(noise) - 50  
            closed_pnl = round(noise * size, 2)

        start_position = round(np.random.normal(0, 2), 4)

        rows.append({
            "account": account,
            "symbol": symbol,
            "execution_price": execution_price,
            "size": size,
            "side": side,
            "time": date.strftime("%Y-%m-%d") + f" {np.random.randint(0,24):02d}:{np.random.randint(0,60):02d}:00",
            "start_position": start_position,
            "event": event,
            "closedPnL": closed_pnl,
            "leverage": leverage,
        })

trader_df = pd.DataFrame(rows)
trader_df.to_csv("data/historical_data.csv", index=False)
print(f"\nWrote {len(trader_df)} rows to data/historical_data.csv")
print(trader_df.head())
