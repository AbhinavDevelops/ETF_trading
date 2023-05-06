import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

# path to csv files
path = "data"

dataframes = {}
volume_dataframes = {}

# calculate volatility and volume for each stock
for filename in os.listdir(path):
    if filename == "VGT.csv" or filename == "IYW.csv" or filename == "SPY.csv":
        continue
    print(filename)
    df = pd.read_csv(path + "/" + filename)

    # Convert the timestamp column to datetime object
    df['time'] = pd.to_datetime(df['time'])

    # Extract the hour from the timestamp
    df['hour'] = df['time'].dt.hour

    # calculate the daily percent change
    df["daily_change"] = df["close"].pct_change()

    # drop the first row
    df = df.iloc[1:]

    # Group by the hour of the day and calculate the standard deviation and mean volume
    hourly_volatility = df.groupby('hour')['daily_change'].std()
    hourly_volume = df.groupby('hour')['volume'].mean()

    # Normalize the hourly volume by dividing it by the total volume of the stock
    total_volume = df['volume'].sum()
    normalized_hourly_volume = hourly_volume / total_volume

    dataframes[filename] = hourly_volatility    
    volume_dataframes[filename] = normalized_hourly_volume
    print(hourly_volatility)

# plot line graph of the average volatility for each stock
volatility_df = pd.DataFrame({k: df for k, df in dataframes.items()})
volatility_df.plot(kind="line", figsize=(15, 8))

# add a title to the plot
plt.title("Average Volatility of Stocks by Hour of the Day")
plt.show()

# plot line graph of the normalized average volume for each stock
normalized_volume_df = pd.DataFrame({k: df for k, df in volume_dataframes.items()})
normalized_volume_df.plot(kind="line", figsize=(15, 8))

# add a title to the plot
plt.title("Normalized Average Volume of Stocks by Hour of the Day")
plt.show()
