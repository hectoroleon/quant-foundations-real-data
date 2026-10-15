"""Download daily prices to data/prices.csv"""

from pathlib import Path

import pandas as pd
import yfinance as yf

SERIES = {
    "^MXX": "IPC",          # Mexican stock index, in pesos (price index, no dividends)
    "EWW": "EWW",           # Mexican market, in dollars
    "MXN=X": "USDMXN_YF",   # Yahoo USD/MXN, only to show its date shift in Module 1
    "SPY": "SPY",
    "EEM": "EEM",
    "TLT": "TLT",
    "IEF": "IEF",
    "GLD": "GLD",
}
START = "2005-01-01"

Path("data").mkdir(exist_ok=True)

raw = yf.download(list(SERIES), start=START, auto_adjust=True, progress=False)
prices = raw["Close"][list(SERIES)].rename(columns=SERIES)

# USD/MXN from FRED (DEXMXUS): noon New York rate, same time of day for the whole history
fred = pd.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXMXUS")
fred = fred.set_index(pd.to_datetime(fred.iloc[:, 0])).iloc[:, 1]
fred = pd.to_numeric(fred, errors="coerce").rename("USDMXN")
prices = prices.join(fred.loc[START:], how="outer")

# markets have different holidays, so we keep every date
prices = prices.dropna(how="all").sort_index()
prices.to_csv("data/prices.csv", float_format="%.6f")

print(f"Saved {prices.shape[0]} days, {prices.index.min().date()} to {prices.index.max().date()}")
for col in prices.columns:
    s = prices[col]
    print(f"  {col:<9} starts {s.first_valid_index().date()}   missing {s.isna().sum():>5}")