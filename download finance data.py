from datetime import datetime, timedelta
import time
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
"""date time convertion code"""
# from datetime import datetime, timedelta
# import time
# ticher = input("Enter the ticker symbol: ")
# from_date = input("Enter start date in yyyy/mm/dd format: ")
# to_date = input("Enter end date in yyyy/mm/dd format: ")

# from_date = datetime.strptime(from_date, "%Y/%m/%d")
# to_date = datetime.strptime(to_date, "%Y/%m/%d")

# from_epoch = int(time.mktime(from_date.timetuple()))
# to_epoch = int(time.mktime(to_date.timetuple()))
"""with this code above be sure to use an F string with '' and {} to make sure the epoch time is inserted correctly"""
