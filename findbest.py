from matplotlib import pyplot as plt
import pandas as pd

# Load the historical stock price data into a Pandas DataFrame
df = pd.read_csv('./data/AAPL.csv')

# Convert the time column to a datetime object and set it as the DataFrame index
df['time'] = pd.to_datetime(df['time'])
df.set_index('time', inplace=True)

unique_days = set()
# Loop through all rows in the DataFrame
for index, row in df.iterrows():
    unique_days.add(index.date())

best_day = None
best_day_percentage_change = 0

for date in unique_days:
    # Select the data for the current day
    day_data = df.loc[str(date)]
    # Define the opening range breakout as the first 30 minutes of trading for the current day
    opening_range = day_data.between_time('9:30', '10:00')
    # Calculate the high and low of the opening range for the current day
    opening_range_high = opening_range['high'].max()


    # highest_price = day_data['high'].max()
    # the highest price should be after 11:00 am
    highest_price = day_data.between_time('11:00', '16:00')['high'].max()

    # Calculate the percentage change of the current day
    percent_change = (highest_price - opening_range_high) / opening_range_high * 100

    # The average price of the stock should be greater than the average price of the opening range for the current day
    average_price = day_data['close'].mean()
    average_opening_range_price = opening_range['close'].mean()


    if average_price > average_opening_range_price and percent_change > best_day_percentage_change:
        print("New best day!")
        print(f"Date: {date} | Opening Range High: {opening_range_high} | Highest Price: {highest_price} | Percent Change: {percent_change}")
        best_day_percentage_change = percent_change
        best_day = date

print(f"The best day was {best_day} with a percentage change of {best_day_percentage_change:.2f}%")

# plots the price of the stock on the best day without the date from 9:30 to 4:00
best_day_data = df.loc[str(best_day)]
# limits the x-axis to the time between 9:30 and 4:00
best_day_data = best_day_data.between_time('9:30', '16:00')
# plots the price of the stock
best_day_data['close'].plot()
plt.show()

# good day is 2022-10-13
