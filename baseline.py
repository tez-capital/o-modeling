import itertools
import numpy as np

import itertools

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

market_wide_average_yield = 0.05 # market wide average yield includes both valuation and rewards yield
long_term_tez_price_trend = 0.04 # how bullish we are - long term price increase per year
build_up_period = 4 # how long to build up stake before launching AI

# Parameters for staking and unstaking
likability_of_staking = 0.01
likability_of_unstaking = 0.01

oslo_dynamic_issuance = 0.00
oslo_maximum_issuance = 0.1075
global oslo_stake_percentage
oslo_stake_percentage = 0.075
oslo_maximum_dynamic_issuance = 0.07
def oslo_static_issuance(x):
    if x == 0:
        return 0
    issuance = 1 / 800 * (1 / x) ** 2
    return max(min(issuance, oslo_maximum_issuance), 0.0005)

oxford_dynamic_issuance = 0.0
oxford_maximum_issuance = 0.05
global oxford_stake_percentage 
oxford_stake_percentage = 0.075
def oxford_static_issuance(x):
    if x == 0:
        return 0
    issuance = 1 / 1600 * (1 / x) ** 2
    return max(min(issuance, oxford_maximum_issuance), 0.0005)


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

def adjust_stake_percentage(stake_percentage, issuance):
    performance = ((issuance + long_term_tez_price_trend) / stake_percentage)
    if performance > market_wide_average_yield:
        stake_percentage += likability_of_staking * (performance - market_wide_average_yield)
    elif performance < market_wide_average_yield:
        stake_percentage -= likability_of_unstaking * (market_wide_average_yield - performance)
    # Ensuring stake percentage remains between 0 and 100
    return max(0, min(stake_percentage, 1))


def data_gen():
    for cnt in itertools.count():
        global oslo_stake_percentage
        global oslo_dynamic_issuance
        global oxford_stake_percentage
        global oxford_dynamic_issuance
        
        t = cnt / 10
        if t == 0:
            continue
        if t < build_up_period: 
            oxford_stake_percentage = adjust_stake_percentage(oslo_stake_percentage, oxford_maximum_issuance)
            oslo_stake_percentage = adjust_stake_percentage(oxford_stake_percentage, oslo_maximum_issuance)
            
            yield t, oslo_stake_percentage, 0, oxford_stake_percentage, 0
        else:
            oslo_dynamic_issuance = dynamic_issuance(oslo_stake_percentage, oslo_dynamic_issuance, oslo_maximum_dynamic_issuance)
            oslo_issuance = oslo_static_issuance(oslo_stake_percentage) + oslo_dynamic_issuance
            oslo_stake_percentage = adjust_stake_percentage(oslo_stake_percentage, oslo_issuance)
            
            oxford_dynamic_issuance = dynamic_issuance(oxford_stake_percentage, oxford_dynamic_issuance, oxford_maximum_issuance)
            oxford_issuance = oxford_static_issuance(oxford_stake_percentage) + oxford_dynamic_issuance
            oxford_stake_percentage = adjust_stake_percentage(oxford_stake_percentage, oxford_issuance)

            yield t, oslo_stake_percentage, oslo_issuance, oxford_stake_percentage, oxford_issuance


def init():
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0, 100)
    del xdata[:]
    del oslo_stake_data[:]
    del oslo_issuance_data[:]
    del oxford_stake_data[:]
    del oxford_issuance_data[:]
    line1.set_data(xdata, oslo_stake_data)
    line2.set_data(xdata, oslo_issuance_data)
    line3.set_data(xdata, oxford_stake_data)
    line4.set_data(xdata, oxford_issuance_data)
    return (
        line1,
        line2,
        line3,
        line4,
    )


fig, ax = plt.subplots()
ax.text(0.05, 0.95, 'market rate ' + str(market_wide_average_yield), transform=ax.transAxes, fontsize=10, va='top')
ax.text(0.05, 0.90, 'price trend ' + str(long_term_tez_price_trend), transform=ax.transAxes, fontsize=10, va='top')
ax.text(0.05, 0.85, 'buildup ' + str(build_up_period), transform=ax.transAxes, fontsize=10, va='top')
(line1,) = ax.plot([], [], lw=2, label="Oslo Issuance %")
(line2,) = ax.plot([], [], lw=2, label="Oslo Stake %")
(line3,) = ax.plot([], [], lw=2, label="Oxford Issuance %")
(line4,) = ax.plot([], [], lw=2, label="Oxford Stake %")
ax.grid()
xdata, oslo_stake_data, oslo_issuance_data, oxford_stake_data, oxford_issuance_data = [], [], [], [], []


def run(data):
    # update the data
    t, oslo_stake, oslo_issuance, oxford_stake, oxford_issuance = data
    xdata.append(t)
    
    oslo_stake_data.append(oslo_stake)
    oslo_issuance_data.append(oslo_issuance)
    oxford_stake_data.append(oxford_stake)
    oxford_issuance_data.append(oxford_issuance)
    
    line1.set_data(xdata, oslo_issuance_data)
    line2.set_data(xdata, oslo_stake_data)
    line3.set_data(xdata, oxford_issuance_data)
    line4.set_data(xdata, oxford_stake_data)
    
    xmin, xmax = ax.get_xlim()
    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()

    return (
        line1,
        line2,
        line3,
    )


# Only save last 100 frames, but run forever
ani = animation.FuncAnimation(
    fig, run, data_gen, interval=5, init_func=init, save_count=1000, repeat=False
)
ax.legend()
# comment out write to see live chart
writer = animation.PillowWriter(fps=20)
ani.save("baseline.gif", writer=writer)

plt.legend()
plt.show()
