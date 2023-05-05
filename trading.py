import os
import random
from matplotlib import pyplot as plt

import numpy as np
from deap import base, creator, tools, algorithms
import datetime

import pandas as pd

num_trades = 0
stock_name = None


def simple_moving_average(prices, window):
    return [sum(prices[i:i + window]) / window for i in range(len(prices) - window + 1)]


def relative_strength(prices, period):
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gains = simple_moving_average(gains, period)
    avg_losses = simple_moving_average(losses, period)

    return [g / l if l != 0 else 0 for g, l in zip(avg_gains, avg_losses)]


def rsi(prices, period):
    rs = relative_strength(prices, period)
    return [100 - (100 / (1 + r)) for r in rs]


def opening_breakout_strategy_native(data, opening_range_minutes, breakout_threshold, rsi_time_period, stop_loss_percent, rsi_value):
    global num_trades, stock_name
    # calculate profit fairly between all stocks of differnet prices
    # buy an equal amount of each stock - 100 / price

    closing_prices = [d['close'] for d in data]
    high_prices = [d['high'] for d in data]
    low_prices = [d['low'] for d in data]

    rsi_values = rsi(closing_prices, rsi_time_period)

    position = 0
    entry_price = None
    intraday_high = None
    intraday_low = None
    trailing_stop = None
    profit_loss = []

    opening_range_high = max(high_prices[:opening_range_minutes])
    opening_range_low = min(low_prices[:opening_range_minutes])

    # Stores the price at which we will enter a position, BUY or SELL, date, and time
    trades = []

    for i in range(opening_range_minutes, len(data) - 1):
        current_rsi = rsi_values[i - rsi_time_period + 1]

        if position == 0:
            if high_prices[i] > opening_range_high * (1 + breakout_threshold) and current_rsi < 50 + rsi_value:
                position = 1
                entry_price = closing_prices[i]
                intraday_high = high_prices[i]
                trades.append((closing_prices[i], 'BUY',i))
            elif low_prices[i] < opening_range_low * (1 - breakout_threshold) and current_rsi > 50 - rsi_value:
                position = -1
                entry_price = closing_prices[i]
                intraday_low = low_prices[i]
                trades.append((closing_prices[i], 'SELL',i))
        else:
            if position == 1:
                intraday_high = max(intraday_high, high_prices[i])
                trailing_stop = intraday_high * (1 - stop_loss_percent)
                if low_prices[i] < trailing_stop or current_rsi > 50 + rsi_value:
                    trades.append((closing_prices[i], 'SELL',i))
                    profit_loss.append(
                        (closing_prices[i] - entry_price) * position)
                    position = 0
            elif position == -1:
                intraday_low = min(intraday_low, low_prices[i])
                trailing_stop = intraday_low * (1 + stop_loss_percent)
                if high_prices[i] > trailing_stop or current_rsi < 50 - rsi_value:
                    trades.append((closing_prices[i], 'BUY',i))
                    profit_loss.append(
                        (closing_prices[i] - entry_price) * position)
                    position = 0
    # close trade if position is still open
    if position != 0:
        profit_loss.append(
            (closing_prices[-1] - entry_price) * position)
        trades.append((closing_prices[-1], 'SELL' if position == 1 else 'BUY',i))

    num_trades += len(trades) // 2

    # # Graphs a line chart of the closing prices
    plt.plot(closing_prices)
    plt.title(stock_name)
    # Plots the trades as dots on the graph
    # for trade in trades:
    #     # green if buy, red if sell
    #     plt.plot(trade[2], trade[0], 'go' if trade[1] == 'BUY' else 'ro')
    plt.xlabel('Minutes')

    # plots hyperparameters
    plt.axhline(y=opening_range_high * (1 + breakout_threshold), color='r', linestyle='-')
    plt.axhline(y=opening_range_low * (1 - breakout_threshold), color='g', linestyle='-')

    # plot the opening range x line dotted faint
    plt.axvline(x=opening_range_minutes, color='b', linestyle='--')

    # in legend, displays the breakout threshold, stop loss percent, and rsi time period
    # plt.legend([
    #     "Opening Range Length: " + str(opening_range_minutes),
    #     'Breakout Threshold: ' + str(breakout_threshold),
    #     'Stop Loss Percent: ' + str(stop_loss_percent),
    #     'RSI Time Period: ' + str(rsi_time_period),
    #     'RSI Value: ' + str(rsi_value)
    # ])
    plt.show()
        
        # divided by average price to get percent change
    return profit_loss / np.mean(closing_prices)


def parse_datetime(date_str):
    # format is year - month - day hour:minute:second
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')


def opening_breakout_strategy_daily(data, opening_range_minutes, breakout_threshold, rsi_time_period, stop_loss_percent,rsi_value):
    data['Datetime'] = data['time'].apply(parse_datetime)
    # .apply(lambda x: x.between_time('9:30', '16:00'))
    data.set_index('Datetime', inplace=True)
    data = data.between_time('9:30', '16:00')

    data_by_day = data.groupby(pd.Grouper(freq='D'))

    profit_loss_by_day = []

    for _, group in data_by_day:
        if not group.empty:
            daily_profit_loss = opening_breakout_strategy_native(
                group.to_dict('records'),
                opening_range_minutes,
                breakout_threshold,
                rsi_time_period,
                stop_loss_percent,
                rsi_value
            )
            profit_loss_by_day.extend(daily_profit_loss)

    return profit_loss_by_day



def grid_search(data):
    # opening_range_minutes_values = [15, 20, 30]
    opening_range_minutes_values = [20]
    # breakout_threshold_values = [0.09,0.1,0.11]
    # breakout_threshold_values = [0.001,0.02,0.03,0.04,0.005,0.006,0.007,0.008,0.009,0.01]
    breakout_threshold_values = [0.005]
    # rsi_time_period_values = [14,21, 28]
    rsi_time_period_values = [28]
    # stop_loss_percent_values = [0.02,0.0225, 0.025]
    stop_loss_percent_values = [0.025]
    rsi_value_values = [40]

    best_profit = float('-inf')
    best_hyperparameters = None

    ranked_hyperparameters = []

    for opening_range_minutes in opening_range_minutes_values:
        for breakout_threshold in breakout_threshold_values:
            for rsi_time_period in rsi_time_period_values:
                for stop_loss_percent in stop_loss_percent_values:
                    for rsi_value in rsi_value_values:
                        daily_profit_loss = opening_breakout_strategy_daily(
                            data,
                            opening_range_minutes,
                            breakout_threshold,
                            rsi_time_period,
                            stop_loss_percent,
                            rsi_value
                        )
                        total_profit_loss = sum(daily_profit_loss)
                        print(f'Parameters: {opening_range_minutes}, {breakout_threshold}, {rsi_time_period}, {stop_loss_percent}, {rsi_value} - Total Profit/Loss: {total_profit_loss:.2f}')

                        ranked_hyperparameters.append({
                            'total_profit_loss': total_profit_loss,
                            'opening_range_minutes': opening_range_minutes,
                            'breakout_threshold': breakout_threshold,
                            'rsi_time_period': rsi_time_period,
                            'stop_loss_percent': stop_loss_percent,
                            "rsi_value":rsi_value
                        })

                        if total_profit_loss > best_profit:
                            best_profit = total_profit_loss
                            best_hyperparameters = {
                                'opening_range_minutes': opening_range_minutes,
                                'breakout_threshold': breakout_threshold,
                                'rsi_time_period': rsi_time_period,
                                'stop_loss_percent': stop_loss_percent,
                                "rsi_value":rsi_value
                            }

    ranked_hyperparameters = sorted(
        ranked_hyperparameters,
        key=lambda x: x['total_profit_loss'],
        reverse=True
    )

    # prints the top 10 hyperparameters
    for hyperparameters in ranked_hyperparameters[:10]:
        print(hyperparameters)
    
    return best_hyperparameters, best_profit

# Read the CSV data
profits = []
directory = './data'
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        stock = filename.replace(".csv","")
        data = pd.read_csv(os.path.join(directory, filename))
        # Run the grid search
        best_hyperparameters, best_profit = grid_search(data)
        profits.append({"stock": filename.replace(".csv",""), "profit": best_profit})
        # Print the best hyperparameters and the corresponding profit
        print(f'Best hyperparameters: {best_hyperparameters}')
        print(f'Best profit: {best_profit:.2f}')
        continue
    else:
        continue

# plots a bar graph of the profits
df = pd.DataFrame(profits)
plt.bar(df['stock'], df['profit'])
plt.ylabel('Profit')
plt.xlabel('Stock')
plt.title('Regularied Profit & Loss')
# show all the hyperparameters on the graph
# plt.legend([
#     "Opening Range Length: " + str(best_hyperparameters['opening_range_minutes']) + " minutes",
#     'Breakout Threshold: ' + str(best_hyperparameters['breakout_threshold']*10) + "%",
#     'Stop Loss Percent: ' + str(best_hyperparameters['stop_loss_percent']*10) + "%",
#     'RSI Time Period: ' + str(best_hyperparameters['rsi_time_period']),
#     'RSI Value: ' + str(best_hyperparameters['rsi_value'])
#     ])
plt.show()

print(profits)
print(sum([x['profit'] for x in profits]))
print(f"Number of trades: {num_trades}")
# data = pd.read_csv('./data/NVDA.csv')

# Run the grid search
# best_hyperparameters, best_profit = grid_search(data)

# Print the best hyperparameters and the corresponding profit
# print(f'Best hyperparameters: {best_hyperparameters}')
# print(f'Best profit: {best_profit:.2f}')