import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load historical data into a Pandas DataFrame
data = pd.read_csv('./data/AAPL.csv')

# date is 2022-10-13

# Convert the time column to a datetime object and set it as the DataFrame index
data['time'] = pd.to_datetime(data['time'])
data.set_index('time', inplace=True)

date = '2022-10-13'
# Select the data for the current day and opening range
day_data = data.loc[str(date)]
day_data = day_data.between_time('9:30', '16:00')
opening_range = day_data.between_time('9:30', '10:00')
opening_range_high = opening_range['close'].max() * 1.0007
opening_range_low = opening_range['close'].min() * 0.9993

# Define a function that updates the chart at each animation frame
def update_chart(i):
    # Select the data for the current animation frame
    current_data = day_data.iloc[:i]
    # Plot the stock price as a line chart with the date on the x-axis and the price on the y-axis
    plt.subplot(2, 1, 1)

    # add a margin between the two subplots
    plt.subplots_adjust(hspace=0.5)

    plt.plot(current_data.index, current_data['close'], color='blue')    
    # Set the chart title and labels
    plt.title('Stock Price and Volume')
    plt.xlabel('Time')
    plt.ylabel('Price')
    # Get the maximum and minimum values of the opening range

    if len(current_data) > 0 and current_data.index[-1].time() >= pd.Timestamp('10:00').time():
        # Get the maximum and minimum values of the opening range
        # Draw horizontal lines at the maximum and minimum values of the opening range
        plt.axhline(y=opening_range_high, color='green', linestyle='--')
        plt.axhline(y=opening_range_low, color='red', linestyle='--')

    # Plot the RSI chart in a subplot below the price chart
    plt.subplot(2, 1, 2)
    # Define the RSI period
    rsi_period = 14
    # Calculate the price change for each period
    price_change = current_data['close'].diff()
    # Calculate the gain and loss for each period
    gain = price_change.where(price_change > 0, 0)
    loss = -price_change.where(price_change < 0, 0)
    # Calculate the average gain and loss over the RSI period
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    # Calculate the relative strength
    rs = avg_gain / avg_loss
    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))
    # Plot the RSI as a line chart
    plt.plot(current_data.index, rsi, color='purple')
    # Set the chart title and labels
    plt.title('Relative Strength Index')
    plt.xlabel('Time')
    plt.ylabel('RSI')
    plt.axhline(y=25, color='green', linestyle='--')
    plt.axhline(y=75, color='red', linestyle='--')



# Create an animation object
animation = FuncAnimation(plt.gcf(), update_chart, frames=len(day_data))

# Save the animation as a video file
animation.save('stock_animation.mp4', writer='ffmpeg')
