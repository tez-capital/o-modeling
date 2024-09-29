import itertools
import numpy as np

import itertools

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

market_rate_min = 0.001
market_rate_max = 0.07

security_target = 0.5

def market_rate(t):
    # Adjust the sine wave to oscillate between 0 and 1
    return (market_rate_max - market_rate_min) / 2 * (np.sin(t / 20 - 1) + 1) + market_rate_min

def price_trend(t):
    return np.random.uniform(-0.02, 0.02)

market_wide_average_yield = 0.05 # market wide average yield includes both valuation and rewards yield

# Parameters for staking and unstaking
likability_of_staking = 0.003
likability_of_unstaking = 0.0015

quebec_dynamic_issuance = 0.01
quebec_maximum_issuance = 0.1
global quebec_stake_percentage
quebec_stake_percentage = 0.2
# (1 + 9 * ((50 - 100 * x) / 42 ) ^ 2 ) / 100
def quebec_maximum_dynamic_issuance(x):
    return (1 + 9 * ((50 - 100 * x) / 42 ) ** 2 ) / 100
    
def quebec_static_issuance(x):
    if x == 0:
        return 0
    issuance = 1 / 1600 * (1 / x) ** 2
    return max(min(issuance, quebec_maximum_issuance), 0.0005)

paris_dynamic_issuance = 0.01
paris_maximum_issuance = 0.1
global paris_stake_percentage 
paris_stake_percentage = 0.2
paris_maximum_dynamic_issuance = 0.05
def paris_static_issuance(x):
    if x == 0:
        return 0
    issuance = 1 / 1600 * (1 / x) ** 2
    return max(min(issuance, paris_maximum_issuance), 0.0005)


def dynamic_issuance(
    stake_percentage, current_dynamic_issuance, maximum_dynamic_issuance
):
    if 0.48 <= stake_percentage <= 0.52:
        return current_dynamic_issuance
    elif stake_percentage < 0.48:
        
        return min(
            current_dynamic_issuance + 0.01 * (0.50 - stake_percentage),
            maximum_dynamic_issuance,
        )
    else:
        return max(current_dynamic_issuance - 0.01 * (stake_percentage - 0.50), 0)

def adjust_stake_percentage(t, stake_percentage, issuance):
    market_wide_average_yield = market_rate(t)
    price_trend_val = price_trend(t)
    performance = ((issuance + price_trend_val) / stake_percentage)
    if performance > market_wide_average_yield:
        stake_percentage += likability_of_staking * (performance - market_wide_average_yield)
    elif performance < market_wide_average_yield:
        stake_percentage -= likability_of_unstaking * (market_wide_average_yield - performance)
    # Ensuring stake percentage remains between 0 and 100
    return max(0, min(stake_percentage, 1))


def data_gen():
    for cnt in itertools.count():
        global quebec_stake_percentage
        global quebec_dynamic_issuance
        global paris_stake_percentage
        global paris_dynamic_issuance
        
        t = cnt / 10
        if t == 0:
            continue

        market_wide_average_yield = market_rate(t)

        quebec_dynamic_issuance = dynamic_issuance(quebec_stake_percentage, quebec_dynamic_issuance, quebec_maximum_dynamic_issuance(quebec_stake_percentage))
        quebec_issuance = quebec_static_issuance(quebec_stake_percentage) + quebec_dynamic_issuance
        quebec_stake_percentage = adjust_stake_percentage(t, quebec_stake_percentage, quebec_issuance)
        
        paris_dynamic_issuance = dynamic_issuance(paris_stake_percentage, paris_dynamic_issuance, paris_maximum_dynamic_issuance)
        paris_issuance = paris_static_issuance(paris_stake_percentage) + paris_dynamic_issuance
        paris_stake_percentage = adjust_stake_percentage(t, paris_stake_percentage, paris_issuance)

        yield t, quebec_stake_percentage, quebec_issuance, paris_stake_percentage, paris_issuance, market_wide_average_yield, security_target


def init():
    ax.set_ylim(0, 0.7)
    ax.set_xlim(0, 300)
    del xdata[:]
    del quebec_stake_data[:]
    del quebec_issuance_data[:]
    del paris_stake_data[:]
    del paris_issuance_data[:]
    del market_rate_data[:]
    del security_target_data[:]
    line1.set_data(xdata, quebec_stake_data)
    line2.set_data(xdata, quebec_issuance_data)
    line3.set_data(xdata, paris_stake_data)
    line4.set_data(xdata, paris_issuance_data)
    line5.set_data(xdata, market_rate_data)
    line6.set_data(xdata, security_target_data)
    return (
        line1,
        line2,
        line3,
        line4,
        line5,
        line6,
    )


fig, ax = plt.subplots()
ax.text(0.05, 0.95, 'market rate 3%', transform=ax.transAxes, fontsize=10, va='top')
ax.text(0.05, 0.90, 'price trend rand -2% to 2%', transform=ax.transAxes, fontsize=10, va='top')
(line1,) = ax.plot([], [], lw=2, label="Quebec Issuance %")
(line2,) = ax.plot([], [], lw=2, label="Quebec Stake %")
(line3,) = ax.plot([], [], lw=2, label="Paris/Qena Issuance %")
(line4,) = ax.plot([], [], lw=2, label="Paris/Qena Stake %")
(line5,) = ax.plot([], [], lw=2, label="Market Rate %")
(line6,) = ax.plot([], [], lw=2, label="Security Target %")
ax.grid()
xdata, quebec_stake_data, quebec_issuance_data, paris_stake_data, paris_issuance_data, market_rate_data, security_target_data = [], [], [], [], [], [], []


def run(data):
    # update the data
    t, quebec_stake, quebec_issuance, paris_stake, paris_issuance, market_rate, security_traget = data
    xdata.append(t)
    plt.legend()
    # plt.show()
    
    quebec_stake_data.append(quebec_stake)
    quebec_issuance_data.append(quebec_issuance)
    paris_stake_data.append(paris_stake)
    paris_issuance_data.append(paris_issuance)
    market_rate_data.append(market_rate)
    security_target_data.append(security_target)
    
    line1.set_data(xdata, quebec_issuance_data)
    line2.set_data(xdata, quebec_stake_data)
    line3.set_data(xdata, paris_issuance_data)
    line4.set_data(xdata, paris_stake_data)
    line5.set_data(xdata, market_rate_data)
    line6.set_data(xdata, security_target_data)

    
    xmin, xmax = ax.get_xlim()
    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()

    return (
        line1,
        line2,
        line3,
        line4,
        line5,
        line6,
    )


# Only save last 100 frames, but run forever
ani = animation.FuncAnimation(
    fig, run, data_gen, interval=10, init_func=init, save_count=3000, repeat=False
)
ax.legend()
# comment out write to see live chart
writer = animation.PillowWriter(fps=20)
ani.save("baseline.gif", writer=writer)

# plt.legend()
# plt.show()
