from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

"""
DataProcessor reads in csv measurements and turns them into processed data.
The data is accessible with DataProcessor.df:
    "time_ms",
    "mT",
    "normalized"

ceil is the mT the coil stabilized at
floor is the measured noise floor (in mT)

get_residuals takes in a DataProcessor and saves the residuals and the residuals of the normalized data and
saves them in DataProcessor.df:
    "residuals"
    "normalized_data_residuals"
"""
class DataProcessor:
    def __init__(self, file: str, ceil_time_range: tuple = (13.0, 15.0), floor_time_range: tuple = (27.5, 30.0), \
        relative_path: str = "msts", legacy: bool = False):

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file = os.path.join(base_dir, relative_path, file)
        if legacy:
            self.df = pd.read_csv(self.file, comment="#")
        else:
            with open(self.file) as f:
                header = f.readline()

            meta = dict(kv.split("=") for kv in header.lstrip("# ").split())
            baseline = float(meta["baseline_counts"])
            # bin_us = int(meta["bin_us"])
            # averages = int(meta["averages"])

            self.df = pd.read_csv(self.file, comment="#")
            self.df["voltage"] = (self.df["value"] - baseline) * 3.3 / 4096 * 1.5 # convert 12-bit number to 5v range
            self.df["mT"] = self.df["voltage"] / 0.03125 # 0.625G * 5v = 3.125mV / G * 10 = 31.25mV/mT

        ceil_start, ceil_end = ceil_time_range
        ceil_filter_df = self.df[
            (self.df["time_ms"] >= ceil_start)
            & (self.df["time_ms"] <= ceil_end)
        ]
        self.ceil = np.mean(ceil_filter_df["mT"]) # ceil is the stable point of the peak current

        floor_start, floor_end = floor_time_range
        floor_filter_df = self.df[
            (self.df["time_ms"] >= floor_start)
            & (self.df["time_ms"] <= floor_end)
        ]
        self.floor = np.mean(floor_filter_df["mT"]) # floor is the stable point of background noise.
        self.noise_stdev = np.std(floor_filter_df["mT"])

        self.df["mT"] = self.df["mT"] - self.floor
        self.df["normalized"] = self.df["mT"] / (self.ceil - self.floor)
        self.ceil_normalized = self.ceil / (self.ceil - self.floor)

    def get_residuals(self, base: DataProcessor, normalized_residuals: bool = True):
        self.df["residuals"] = self.df["mT"] - base.df["mT"]
        self.df["normalized_data_residuals"] = self.df["normalized"] - base.df["normalized"]


"""
The signal plot function takes in a DataProcessor and then plots it within the specificied
time and y_range.
Time_range is in ms.
Normalize uses the normalized signal based on the ceil and the floor of the DataProcessor.
"""
def plot_signal(data: DataProcessor, time_range: tuple = (0.0, 30.0), normalize: bool = True, \
    label: str = "", ms_offset: float = 0.0):
    data.df["time_ms"] = data.df["time_ms"] + ms_offset

    min_time, max_time = time_range
    filtered_data_df = data.df[
            (data.df["time_ms"] >= min_time)
            & (data.df["time_ms"] <= max_time)
    ]

    normalized_label = "normalized" if normalize else "mT"

    if label == "":
        label = data.file

    plt.plot(filtered_data_df["time_ms"], filtered_data_df[normalized_label], label=label)

    ### Deprecated, may be added again later. ###
    # if not plot_fit_lines: return

    # floor_start = max(floor_time_range[0], min_time_plot)
    # floor_end = min(floor_time_range[1], max_time_plot)

    # if floor_start <= floor_end:
    #     plt.hlines(0.0, floor_start, floor_end, colors="red")

    # ceil_start = max(ceil_time_range[0], min_time_plot)
    # ceil_end = min(ceil_time_range[1], max_time_plot)

    # if ceil_start <= ceil_end:
    #     plt.hlines(data.ceil_normalized, ceil_start, ceil_end, colors="red", label="decay point")


"""
bin_residuals merges data from x amount of bins into 1 bin, its used to increase the signal-to-noise ratio by sacrificing time resolution
bin_n is the amount of bins that will be merged into one. To calculate the new time resolution you simply divide the previous time resolution by bin_n.
"""
def bin_residuals(residuals: DataProcessor, bin_n: int = 5, normalized_data: bool = True) -> pd.DataFrame:
    # average groups of bin_n samples (5 x 5 us = 25 us bins)
    n = len(residuals.df) // bin_n * bin_n
    t = residuals.df["time_ms"].to_numpy()[:n].reshape(-1, bin_n).mean(axis=1)

    r = None
    if normalized_data:
        r = residuals.df["normalized_data_residuals"].to_numpy()[:n].reshape(-1, bin_n).mean(axis=1)
    else:
        r = residuals.df["residuals"].to_numpy()[:n].reshape(-1, bin_n).mean(axis=1)

    return pd.DataFrame({"time_ms": t, "residuals": r})


"""
plot_residuals plots the residuals of the selected DataProcessor.
normalized_data selects wether to use the raw "mT" column of the DataProcessor.df or the "normalized" column
normalize selects if the binned data should be normalized
bin_n is the amount of bins that will be merged into one. (look at def bin_residuals for details)
"""
def plot_residuals(data: DataProcessor, label: str = "", normalized_data: bool = True, normalize: bool = True, bin_n=5, time_range: tuple = (15.0, 30.0)):
    binned_res: pd.DataFrame = (bin_residuals(data, bin_n, normalized_data = normalized_data))
    if normalize:
        binned_res["residuals"] = binned_res["residuals"] / binned_res["residuals"].max() # linear scaling based on peak since our data floor is already centered at 0.0

    min_time, max_time = time_range
    binned_res_time_filtered = binned_res[
        (binned_res["time_ms"] >= min_time)
        & (binned_res["time_ms"] <= max_time)
    ]

    if label == "":
        label = data.file

    plt.plot(binned_res_time_filtered["time_ms"], binned_res_time_filtered["residuals"], label=label)


# TODO: implement into final fit
def fit_decay(res, t0=15.0, start=1.0, end=10.0):
    d = res[(res["time_ms"] >= t0 + start) & (res["time_ms"] <= t0 + end)]
    popt, _ = curve_fit(
        lambda t, a, tau: a * np.exp(-(t - t0) / tau),
        d["time_ms"], d["res"], p0=(0.02, 2.0),
    )
    return popt  # (amplitude, tau in ms)


def exp_h(x, a, b, c):
    return a * np.exp(-(x-c) * b).astype(float)
