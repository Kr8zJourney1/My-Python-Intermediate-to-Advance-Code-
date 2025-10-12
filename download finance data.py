from datetime import datetime, timedelta
import pandas as pd
import pandas_datareader.data as web

symbol = "AAPL"

# Last ~18 months (548 days ≈ 1.5 years)
end = datetime.today()
start = end - timedelta(days=548)

# Fetch from Stooq (returns newest-first → sort ascending)
df = web.DataReader(symbol, "stooq", start=start, end=end).sort_index()

# Save to CSV with dates in the filename
out = f"{symbol}_stooq_{start:%Y%m%d}-{end:%Y%m%d}.csv"
df.to_csv(out, index=True)

print(f"Saved {len(df)} rows to {out}")
print(df.head(), "\n...\n", df.tail())


"""Second version without pandas_datareader"""
# symbol = "AAPL"
# end   = datetime.today()
# start = end - timedelta(days=548)

# url = f"https://stooq.com/q/d/l/?s={symbol.lower()}&i=d"
# df  = pd.read_csv(url, parse_dates=["Date"]).sort_values("Date")
# df  = df[(df["Date"] >= start) & (df["Date"] <= end)]

# df.to_csv(f"{symbol}_stooq_{start:%Y%m%d}-{end:%Y%m%d}.csv", index=False)
