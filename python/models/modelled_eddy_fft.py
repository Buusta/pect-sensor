import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as fft
from scipy.optimize import least_squares

from core import pect


def eddy_model(time, B, tau_ms, gain):
    """Eddy-current field: exponentially decaying response to dB/dt."""
    eddy = np.zeros(len(B))
    dt, dB = np.diff(time), np.diff(B)
    decay = np.exp(-dt / tau_ms)
    for i in range(1, len(B)):
        eddy[i] = eddy[i - 1] * decay[i - 1] - gain * dB[i - 1]
    return eddy


def fit_eddy(time, B, residual, window, p0=(1.5, 0.04)):
    mask = (time >= window[0]) & (time <= window[1])
    res = least_squares(
        lambda p: (eddy_model(time, B, *p) - residual)[mask],
        x0=p0,
        bounds=([1e-3, -np.inf], [100.0, np.inf]),
        x_scale=[1.0, 0.01],
    )
    return res.x


calibration_df = pect.read_mst("calibration_11.csv")
calibration = pect.DataProcessor(calibration_df)

measurement_df = pect.read_mst("measurement_11.csv")
measurement = pect.DataProcessor(measurement_df)

time = calibration.df["time_ms"].to_numpy()
B = calibration.df["normalized"].to_numpy()
c = calibration.ceil

tau = 0.4
k = 0.2

eddy = eddy_model(time, B, tau, k)

time_mask = (time >= 15.0) & (time <= 30.0)

sample_rate = 200e3
N = len(eddy[time_mask])

xf = fft.rfftfreq(N, 1.0 / sample_rate)
yf = fft.rfft(eddy[time_mask])

frequency_mask = xf <= 6e3

plt.grid(True)
plt.plot(time, eddy)
plt.plot(time, measurement.df["normalized_data_residuals"])
# plt.plot(xf[frequency_mask], np.abs(yf[frequency_mask]))
plt.savefig("signal.png")
plt.show()
