import itertools
import pandas as pd

def calculate_profit(breakout_opportunities):
    profit = 0
    position = None

    for _, row in breakout_opportunities.iterrows():
        if row['breakout']:
            if position is None:
                position = row['close']
            else:
                profit += row['close'] - position
                position = None

    return profit

# Hyperparameters ranges
opening_range_minutes_options = [i for i in range(15, 60+1, 5)]
# breakout threshold is 0.1 ... 2.5
breakout_threshold_options = [i / 100 for i in range(10, 250+1, 5)]
# Read the data
file = "data/AAPL.csv"

# Load the data into a pandas DataFrame
df = pd.read_csv(file, parse_dates=['time'])
df.set_index('time', inplace=True)

# Grid search for optimal hyperparameters
best_hyperparameters = None
best_profit = float('-inf')

for opening_range_minutes, breakout_threshold in itertools.product(opening_range_minutes_options, breakout_threshold_options):
    print("Evaluating hyperparameters: opening_range_minutes={}, breakout_threshold={}".format(opening_range_minutes, breakout_threshold))
    opening_range_start = df.index.min()
    opening_range_end = opening_range_start + pd.Timedelta(minutes=opening_range_minutes)

    opening_range = df.loc[opening_range_start:opening_range_end]

    opening_range_high = opening_range['high'].max()
    opening_range_low = opening_range['low'].min()

    breakout_threshold_high = opening_range_high * (1 + breakout_threshold / 100)
    breakout_threshold_low = opening_range_low * (1 - breakout_threshold / 100)

    breakout_opportunities = df.loc[opening_range_end + pd.Timedelta(minutes=1):].copy()
    breakout_opportunities['breakout'] = False

    breakout_opportunities.loc[breakout_opportunities['high'] > breakout_threshold_high, 'breakout'] = True
    breakout_opportunities.loc[breakout_opportunities['low'] < breakout_threshold_low, 'breakout'] = True

    profit = calculate_profit(breakout_opportunities[breakout_opportunities['breakout']])
    
    print("Profit: ${:.2f}".format(profit)) 
    if profit > best_profit:
        best_profit = profit
        best_hyperparameters = (opening_range_minutes, breakout_threshold)

print("Optimal hyperparameters:")
print("Opening range duration (minutes):", best_hyperparameters[0])
print("Breakout threshold (percentage):", best_hyperparameters[1])
print("Total profit:", best_profit)