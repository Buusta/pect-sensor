import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks


class Data:
    def __init__(self, file: str):
        self.file = file
        self.df = pd.read_csv(self.file)

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

        print(round(self.decay_time - current_turn_off_time, 2), "ms")


def exp_h(x, a, b, c):
    return a * np.exp(-(x-c) * b).astype(float)


def plot_data(data: Data):
    filtered_data_df = data.df[
            (data.df["time_ms"] >= min_time_plot)
            & (data.df["time_ms"] <= max_time_plot)
    ]

    normalized_label = "normalized" if normalized_plot else "mT"

    label = data.file
    plt.plot(filtered_data_df["time_ms"], filtered_data_df[normalized_label], label=label)
    
    plt.scatter(data.decay_time, data.decay_value, color="red", zorder=10)

    if not plot_fit_lines: return

    floor_start = max(floor_time_range[0], min_time_plot)
    floor_end = min(floor_time_range[1], max_time_plot)

    if floor_start <= floor_end:
        plt.hlines(0.0, floor_start, floor_end, colors="red")

    ceil_start = max(ceil_time_range[0], min_time_plot)
    ceil_end = min(ceil_time_range[1], max_time_plot)

    if ceil_start <= ceil_end:
        plt.hlines(data.ceil_normalized, ceil_start, ceil_end, colors="red", label="decay point")


normalized_plot: bool = True
plot_fit_lines: bool = False
min_time_plot: float = 19.0
max_time_plot: float = 25.0
fit_line_resolution = 100
linewidth: float = 2.0

floor_time_range = (35.0, 70.0)
ceil_time_range = (10.0, 20.0)
current_turn_off_time: float = 20.0
decay_threshold = 0.01




# calibration = Data("new_setup/calibration.csv")
# t5mm = Data("new_setup/t5mm.csv")

# residuals_df = pd.DataFrame()
# residuals_df["time_ms"] = calibration.df["time_ms"]
# residuals_df["residuals"] = t5mm.df["normalized"] - calibration.df["normalized"]

# residuals_filter_df = residuals_df[
#     (residuals_df["time_ms"] >= 19.0)
#     & (residuals_df["time_ms"] <= 30.0)
# ]

# plt.plot(residuals_filter_df["time_ms"], residuals_filter_df["residuals"])

# t5mm_d10mm = Data("msts_peak/3mm_10mm_dist.csv", normalize)
# t5mm_d2mm = Data("msts_peak/3mm_2mm_dist.csv", normalize)
setup_1 = Data("setup_1.csv")
# setup_2 = Data("setup_2.csv")
# setup_3 = Data("setup_3.csv")
setup_4 = Data("setup_4.csv")
setup_5 = Data("setup_5.csv")

# plot_data(setup_1)
plot_data(setup_1)
plot_data(setup_5)

# plot_data(setup_1, False)
# plot_data(setup_2, False)
# plot_data(setup_3, False)
# plot_data(setup_4, False)

#plt.plot(calibration.df["time_ms"], calibration.df["normalized"])

# msts2 = pd.DataFrame()
# msts2["peak"] = t5mm_d10mm.df[t5mm_d10mm.y_column] - calibration.df[calibration.y_column]
# msts2["peak2"] = t5mm_d2mm.df[t5mm_d2mm.y_column] - calibration.df[calibration.y_column]
# #plt.plot(calibration.df["time_ms"], msts2["peak"], label="t5.0 d10.0")
# plt.plot(calibration.df["time_ms"], msts2["peak2"], label="t5.0 d2.0")


# peaks = find_peaks(msts2["peak2"], threshold=0.002)[0][-1]
# peaks_x = calibration.df["time_ms"].iloc[peaks]
# peaks_y = msts2["peak2"].iloc[peaks]

# plt.scatter(peaks_x, peaks_y)

# falloff_data = msts2["peak2"][calibration.df["time_ms"] >= peaks_x]
# fallof_time = calibration.df["time_ms"][calibration.df["time_ms"] >= peaks_x]

# plt.plot(fallof_time, falloff_data, label="t5.0 d2.0")

# def exp(x, a, b, c):
#     return a * np.exp(-(x-c) * b).astype(float)

# p_init = [261.0, 0.92, 13.0]
# p_limit = ([100.0, 0.6, 8.0], [300.0, 1.2, 20.0])

# popt, pcov = curve_fit(exp, fallof_time, falloff_data, p0=p_init, bounds=p_limit)

# print(1.0 / popt[1])

# x = np.linspace(peaks_x, max_time, 1000)
# y = exp(x, popt[0], popt[1], popt[2])

# plt.plot(x, y)

#plt.scatter()

plt.legend()
plt.grid(True)
plt.savefig("setups.png", dpi=100)
plt.show()