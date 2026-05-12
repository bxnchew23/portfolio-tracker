"""
Daily price updater — run by GitHub Actions.
Fetches latest prices for all portfolio tickers using yfinance
and writes them to prices.json for the GitHub Pages site to read.
"""

import json
import yfinance as yf
from datetime import datetime, timezone

TICKERS = [
    # USD stocks
    "AAPL", "AMZN", "CQQQ", "GOOGL", "LKNCY",
    "NVDA", "SPY", "TSM", "VOO",
    # SGD stocks (Singapore Exchange)
    "AJBU.SI", "D05.SI", "ME8U.SI", "N2IU.SI",
]

SGD_USD_TICKER = "SGDUSD=X"


def fetch_prices():
    all_tickers = TICKERS + [SGD_USD_TICKER]
    print(f"Fetching {len(all_tickers)} tickers...")

    data = yf.download(
        tickers=all_tickers,
        period="2d",
        interval="1d",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
    )

    prices = {}
    sgd_usd_rate = 0.78931  # fallback

    for ticker in all_tickers:
        try:
            if len(all_tickers) == 1:
                ticker_data = data
            else:
                ticker_data = data[ticker]

            closes = ticker_data["Close"].dropna()
            if len(closes) < 1:
                print(f"  No data for {ticker}")
                continue

            last_price = float(closes.iloc[-1])
            prev_price = float(closes.iloc[-2]) if len(closes) >= 2 else last_price
            change = last_price - prev_price
            change_pct = (change / prev_price * 100) if prev_price else 0

            if ticker == SGD_USD_TICKER:
                sgd_usd_rate = round(last_price, 5)
                print(f"  SGD/USD rate: {sgd_usd_rate}")
            else:
                prices[ticker] = {
                    "price":     round(last_price, 4),
                    "change":    round(change, 4),
                    "changePct": round(change_pct, 4),
                    "ts":        int(datetime.now(timezone.utc).timestamp() * 1000),
                }
                print(f"  {ticker}: {last_price:.4f} ({change_pct:+.2f}%)")

        except Exception as e:
            print(f"  Error fetching {ticker}: {e}")

    return prices, sgd_usd_rate


def main():
    prices, sgd_usd_rate = fetch_prices()

    output = {
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sgdUsdRate":  sgd_usd_rate,
        "prices":      prices,
    }

    with open("prices.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. Updated {len(prices)} tickers. SGD/USD = {sgd_usd_rate}")
    print(f"prices.json written at {output['lastUpdated']}")


if __name__ == "__main__":
    main()
