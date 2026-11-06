import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
import os


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


"""
DataProcessor reads in csv measurements and turns them into processed data.
The raw data can be accessed trough DataProcessor.df.
Legacy uses an old way to read in csv so they can be compared with new measurements.
Ceil is the stable point of the peak current, the time range is used for normalizing it to 1.0.
Floor is the stable point of background noise, the time range is used for normalizing it to 0.0.
"""
class DataProcessor:
    def __init__(self, file: str, ceil_time_range: tuple = (13.0, 15.0), floor_time_range: tuple = (27.5, 30.0), \
        relative_path: str = "msts", legacy: bool = False):

        self.file = file_path = os.path.join(base_dir, relative_path, file)
        if legacy:
            self.df = pd.read_csv(self.file, comment="#")
        else:
            with open(self.file) as f:
                header = f.readline()

            meta = dict(kv.split("=") for kv in header.lstrip("# ").split())
            baseline = float(meta["baseline_counts"])
            bin_us = int(meta["bin_us"])
            averages = int(meta["averages"])

            self.df = pd.read_csv(self.file, comment="#")
            self.df["voltage"] = (self.df["value"] - baseline) / 4095 * 5.0 # convert 12-bit number to 5v
            self.df["mT"] = (self.df["voltage"] - 2047) / 0.003125 # 0.625G * 5v = 3.125mV / G * 10 = 31.25mV/mT

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


"""
The signal plot function takes in a DataProcessor and then plots it within the specificied
time and y_range.
Time_range is in ms.
Y_range is in mT, it will automatically be converted to a.u. if normalize is True.
Normalize uses the normalized signal based on the ceil and the floor of the DataProcessor.
"""
def plot_signal(data: DataProcessor, time_range: tuple = (0.0, 30.0), y_range: tuple = (0.0, 10.0), normalize: bool = True, \
    label: str = ""):
    data.df["time_ms"] = data.df["time_ms"] + ms_offset

    min_time, max_time = time_range
    filtered_data_df = data.df[
            (data.df["time_ms"] >= min_time_plot)
            & (data.df["time_ms"] <= max_time_plot)
    ]

    y_min, y_max = y_range
    if normalize:
        y_min = (y_min - data.floor) / (data.ceil - data.floor)
        y_max = (y_max - data.floor) / (data.ceil - data.floor)

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
Get_residuals gets the residuals of the calibration DataProcesor and the measurement DataProcessor

"""
def get_residuals(calibration: DataProcessor, measurement: DataProcessor, normalize: bool = True) -> DataFrame:
    df = pd.DataFrame()
    df["time_ms"] = calibration.df["time_ms"]

    normalize_label: str = "noralized" if normalize else "mT"

    df["res"] = measurement.df[normalize_label] - calibration.df[normalize_label]
    return df


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



def exp_h(x, a, b, c):
    return a * np.exp(-(x-c) * b).astype(float)


# normalized_plot: bool = True
# plot_fit_lines: bool = False
# min_time_plot: float = 0.0
# max_time_plot: float = 30.0
# fit_line_resolution = 100
# linewidth: float = 2.0

# floor_time_range = (27.5, 30.0)
# ceil_time_range = (13.0, 15.0)
# current_turn_off_time: float = 20.0
# decay_threshold = 0.01