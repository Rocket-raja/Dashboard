"""Fetch market snapshot data (free, via yfinance) and write data.json.

Run:  pip install yfinance && python fetch_data.py
Edit the GROUPS list below to change what the dashboard shows.
"""
import json
import sys
import datetime as dt

import yfinance as yf

GROUPS = [
    ("us", "US close", [
        ("^DJI", "Dow Jones"), ("^GSPC", "S&P 500"), ("^IXIC", "Nasdaq"), ("^VIX", "US VIX"),
    ]),
    ("fut", "US futures", [
        ("ES=F", "S&P 500 futures"), ("NQ=F", "Nasdaq futures"), ("YM=F", "Dow futures"),
    ]),
    ("asia", "Asia", [
        ("^N225", "Nikkei 225"), ("^HSI", "Hang Seng"), ("000001.SS", "Shanghai"),
        ("^KS11", "KOSPI"), ("^AXJO", "ASX 200"), ("^STI", "Straits Times"),
    ]),
    ("eu", "Europe", [
        ("^FTSE", "FTSE 100"), ("^GDAXI", "DAX"), ("^FCHI", "CAC 40"), ("^STOXX50E", "Euro Stoxx 50"),
    ]),
    ("india", "India", [
        ("^NSEI", "Nifty 50"), ("^NSEBANK", "Bank Nifty"), ("^BSESN", "Sensex"), ("^INDIAVIX", "India VIX"),
    ]),
    ("macro", "Commodities, FX, yields", [
        ("BZ=F", "Brent crude"), ("CL=F", "WTI crude"), ("GC=F", "Gold"), ("SI=F", "Silver"),
        ("INR=X", "USD/INR"), ("DX-Y.NYB", "Dollar index"), ("^TNX", "US 10Y yield"),
    ]),
    # Put your own global stocks here
    ("watch", "My watchlist", [
        ("AAPL", "Apple"), ("MSFT", "Microsoft"), ("NVDA", "Nvidia"),
        ("TSLA", "Tesla"), ("AMZN", "Amazon"), ("GOOGL", "Alphabet"),
    ]),
]


def quote(symbol):
    hist = yf.Ticker(symbol).history(period="7d", interval="1d", auto_adjust=False)
    closes = hist["Close"].dropna()
    if len(closes) < 2:
        return None
    last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
    return {
        "price": round(last, 4),
        "change": round(last - prev, 4),
        "pct": round((last - prev) / prev * 100, 3) if prev else None,
        "asof": closes.index[-1].strftime("%d %b"),
    }


def main():
    out, ok, total = [], 0, 0
    for gid, title, items in GROUPS:
        rows = []
        for symbol, name in items:
            total += 1
            row = {"symbol": symbol, "name": name, "price": None, "change": None, "pct": None, "asof": None}
            try:
                q = quote(symbol)
                if q:
                    row.update(q)
                    ok += 1
                else:
                    print(f"no data: {symbol}", file=sys.stderr)
            except Exception as e:  # keep going if one symbol fails
                print(f"failed: {symbol}: {e}", file=sys.stderr)
            rows.append(row)
        out.append({"id": gid, "title": title, "items": rows})

    if ok == 0:
        sys.exit("No symbols returned data; keeping the old data.json")

    payload = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "groups": out}
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print(f"Wrote data.json ({ok}/{total} symbols)")


if __name__ == "__main__":
    main()
