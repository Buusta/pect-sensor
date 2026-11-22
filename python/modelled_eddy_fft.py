import matplotlib.pyplot as plt
import numpy as np
import pect
from scipy.optimize import least_squares
import scipy.fft as fft


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


processor = pect.DataProcessor("new_mst.csv")
time = processor.df["time_ms"].to_numpy()
B = processor.df["normalized"].to_numpy()
c = processor.ceil

tau = 3.0
k = 1.0

eddy = eddy_model(time, B, tau, k) * 0.1

time_mask = (time >= 15.0) & (time <= 30.0)

sample_rate = 200e3
N = len(eddy[time_mask])

xf = fft.rfftfreq(N, 1.0 / sample_rate)
yf = fft.rfft(eddy[time_mask])

frequency_mask = (xf <= 6e3)

plt.grid(True)
# plt.plot(time[time_mask], eddy[time_mask])
plt.plot(xf[frequency_mask], np.abs(yf[frequency_mask]))
plt.show()
