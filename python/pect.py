import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import os


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sensitivity = 0.003115

class Data:
    def __init__(self, file: str, legacy: bool = False):
        self.file = file_path = os.path.join(base_dir, "msts", file)
        if legacy:
            self.df = pd.read_csv(self.file, comment="#")
        else:
            with open(self.file) as f:
                header = f.readline()          # "# baseline_counts=2051.347 cal_ms=1000 ..."

            meta = dict(kv.split("=") for kv in header.lstrip("# ").split())
            baseline = float(meta["baseline_counts"])
            bin_us = int(meta["bin_us"])
            averages = int(meta["averages"])

            self.df = pd.read_csv(self.file, comment="#")
            self.df["voltage"] = (self.df["value"] - baseline) * 3.3 / 4096 * 1.5
            self.df["mT"] = self.df["voltage"] / 0.03115

        floor_start, floor_end = floor_time_range
        floor_filter_df = self.df[
            (self.df["time_ms"] >= floor_start)
            & (self.df["time_ms"] <= floor_end)
        ]
        self.floor = np.mean(floor_filter_df["mT"])

        ceil_start, ceil_end = ceil_time_range
        ceil_filter_df = self.df[
            (self.df["time_ms"] >= ceil_start)
            & (self.df["time_ms"] <= ceil_end)
        ]
        self.ceil = np.mean(ceil_filter_df["mT"])

        self.df["mT"] = self.df["mT"] - self.floor
        self.df["normalized"] = self.df["mT"] / (self.ceil - self.floor)
        self.ceil_normalized = self.ceil / (self.ceil - self.floor)

        crossings = self.df.loc[
            (self.df["normalized"] <= decay_threshold)
            & (self.df["time_ms"] > current_turn_off_time),
            ["time_ms", "normalized"]
        ]

        if not crossings.empty:
            self.decay_time = crossings.iloc[0]["time_ms"]
            self.decay_value = crossings.iloc[0]["normalized"]
        else:
            self.decay_time = None
            self.decay_value = None

        # print(round(self.decay_time - current_turn_off_time, 2), "ms")


def exp_h(x, a, b, c):
    return a * np.exp(-(x-c) * b).astype(float)


def plot_data(data: Data, ms_offset: float = 0.0, normalize=True):
    data.df["time_ms"] = data.df["time_ms"] + ms_offset

    filtered_data_df = data.df[
            (data.df["time_ms"] >= min_time_plot)
            & (data.df["time_ms"] <= max_time_plot)
    ]

    normalized_label = "normalized" if normalize else "mT"

    label = data.file
    plt.plot(filtered_data_df["time_ms"], filtered_data_df[normalized_label], label=label)
    
    # plt.scatter(data.decay_time, data.decay_value, color="red", zorder=10)

    if not plot_fit_lines: return

    floor_start = max(floor_time_range[0], min_time_plot)
    floor_end = min(floor_time_range[1], max_time_plot)

    if floor_start <= floor_end:
        plt.hlines(0.0, floor_start, floor_end, colors="red")

    ceil_start = max(ceil_time_range[0], min_time_plot)
    ceil_end = min(ceil_time_range[1], max_time_plot)

    if ceil_start <= ceil_end:
        plt.hlines(data.ceil_normalized, ceil_start, ceil_end, colors="red", label="decay point")


def residuals(calibration: DataFrame, measurement: DataFrame) -> DataFrame:
    df = pd.DataFrame()
    df["time_ms"] = calibration["time_ms"]
    df["res"] = measurement["normalized"] - calibration["normalized"]
    return df

zed = 10

def bin_residuals(residuals: DataFrame, bin_n: int = 5) -> DataFrame:
    # average groups of bin_n samples (5 x 5 us = 25 us bins)
    n = len(residuals) // bin_n * bin_n
    t = residuals["time_ms"].to_numpy()[:n].reshape(-1, bin_n).mean(axis=1)
    r = residuals["res"].to_numpy()[:n].reshape(-1, bin_n).mean(axis=1)
    return pd.DataFrame({"time_ms": t, "res": r})


def plot_residuals(residuals: DataFrame, label=None, bin_n=5, normalize=True,
                   log=False, t_off=15.0, from_peak=True):
    global zed
    df = (bin_residuals(residuals, bin_n) if bin_n > 1 else residuals).copy()

    smooth = df["res"].rolling(8, center=True).mean()
    peak_i = smooth[df["time_ms"] >= t_off].idxmax()
    peak_t = df.loc[peak_i, "time_ms"]

    if normalize:
        df["res"] = df["res"] / smooth[peak_i]  # scale before cutting
    if from_peak:
        df = df[df["time_ms"] >= peak_t]

    mask = (df["time_ms"] >= min_time_plot) & (df["time_ms"] <= max_time_plot)
    plt.plot(df["time_ms"][mask], df["res"][mask], label=label, zorder=zed)
    zed -= 1

    if log:
        plt.yscale("log")
    return peak_t


def fit_decay(res, t0=15.0, start=1.0, end=10.0):
    d = res[(res["time_ms"] >= t0 + start) & (res["time_ms"] <= t0 + end)]
    popt, _ = curve_fit(
        lambda t, a, tau: a * np.exp(-(t - t0) / tau),
        d["time_ms"], d["res"], p0=(0.02, 2.0),
    )
    return popt  # (amplitude, tau in ms)


normalized_plot: bool = True
plot_fit_lines: bool = False
min_time_plot: float = 0.0
max_time_plot: float = 30.0
fit_line_resolution = 100
linewidth: float = 2.0

floor_time_range = (27.5, 30.0)
ceil_time_range = (13.0, 15.0)
current_turn_off_time: float = 20.0
decay_threshold = 0.01