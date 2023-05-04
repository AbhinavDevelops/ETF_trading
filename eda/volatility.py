import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

# path to csv files
path = "data"

dataframes = {}
# calculate volatility for each stock
for filename in os.listdir(path):
    print(filename)
    df = pd.read_csv(path + "/" + filename)
    # calculate the daily percent change
    df["daily_change"] = df["close"].pct_change()

    # drop the first row
    df = df.iloc[1:]

    # calculate the daily standard deviation
    df["volatility"] = df["daily_change"].rolling(21).std()

    dataframes[filename] = df

# plot bar graph of the average volatility for each stock
volatility = {k: df["volatility"].mean() for k, df in dataframes.items()}
volatility_df = pd.DataFrame.from_dict(volatility, orient="index")
volatility_df.columns = ["volatility"]
volatility_df.sort_values(by="volatility", inplace=True)
volatility_df.plot(kind="bar", figsize=(15, 8))
plt.show()

# create a DataFrame with the volatility data
volatility_df = pd.DataFrame({k: df["volatility"] for k, df in dataframes.items()})

# calculate the correlation matrix
corr_matrix = volatility_df.corr()


sns.heatmap(corr_matrix, cmap="coolwarm", annot=True, fmt=".2f")
plt.show()