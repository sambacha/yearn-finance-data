import pandas as pd
import lib
import pickle

df = lib.read_date_range(start_date="2017-01-01", end_date="2017-12-31")
df = df[df.SecurityType == "Common stock"]
df.set_index("CalcDateTime", drop=True, inplace=True)
df = df.between_time("08:00", "20:00")
df = df[df.TradedVolume > 0]
with open("securities.txt", "rb") as f:
    securities = pickle.load(f)
df = df[df["Mnemonic"].isin(securities)]
df.to_parquet("../data/processed_data/20200904/top100stocks_cleaned_2017.parquet")
