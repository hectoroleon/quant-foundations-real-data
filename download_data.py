"""
Download the daily price data used in the notebooks.

Run it once from the repo folder:
    pip install yfinance pandas
    python download_data.py

It creates data/prices.csv with adjusted closes (dividends and splits included
where Yahoo has them), one column per series. The notebooks only read that file,
so they run offline after this.

The point of view is a Mexican saver: the Mexican market in pesos, the same
market in dollars, the peso itself, and the US and global assets that a person
in Mexico can actually buy.
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

SERIES = {
    # Mexico
    "^MXX": "IPC",        # S&P/BMV IPC, main Mexican stock index, in pesos (price index, no dividends)
    "EWW": "EWW",         # iShares MSCI Mexico ETF, the Mexican market measured in dollars
    "MXN=X": "USDMXN",    # pesos per one US dollar
    # US and global, in dollars
    "SPY": "SPY",         # US stocks (S&P 500)
    "EEM": "EEM",         # emerging markets, to compare Mexico against its peers
    "TLT": "TLT",         # long US Treasuries (20+ years)
    "IEF": "IEF",         # 7-10 year US Treasuries
    "GLD": "GLD",         # gold
}
START = "2005-01-01"
END = None  # None means up to the last available day

out_dir = Path("data")
out_dir.mkdir(exist_ok=True)

raw = yf.download(list(SERIES), start=START, end=END, auto_adjust=True, progress=False)
prices = raw["Close"][list(SERIES)].rename(columns=SERIES)

# Mexico and the US do not share holidays, and the peso trades almost every day,
# so I keep every date and leave NaN where a market was closed. Each notebook
# aligns the series it needs instead of deleting days here.
prices = prices.dropna(how="all").sort_index()

prices.to_csv(out_dir / "prices.csv", float_format="%.6f")

print(f"Saved {prices.shape[0]} days x {prices.shape[1]} series to data/prices.csv")
print(f"From {prices.index.min().date()} to {prices.index.max().date()}\n")
print("First date and missing values per series:")
for col in prices.columns:
    s = prices[col]
    print(f"  {col:<7} starts {s.first_valid_index().date()}   missing {s.isna().sum():>5}")