import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
import pect


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
        x0=p0, bounds=([1e-3, -np.inf], [100.0, np.inf]), x_scale=[1.0, 0.01],
    )
    return res.x


calibration = pect.Data("modelling/calibration.csv")
d5mm = pect.Data("modelling/t5mm.csv")

time = calibration.df["time_ms"].to_numpy()
B = calibration.df["normalized"].to_numpy()
residual = d5mm.df["normalized"].to_numpy() - B
c = calibration.ceil

fit_window = (17.0, 21.0)
tau, k = fit_eddy(time, B, residual, fit_window)
eddy = eddy_model(time, B, tau, k)
print(f"tau = {tau:.3f} ms, k = {k:.4f}")

# Plot 1: calibration with modelled eddy field
plt.figure(figsize=(8, 4))
plt.plot(time, B * c, label="Kalibratie veld")
plt.plot(time, eddy * c, color="tab:green", label="Gemodelleerd Eddy current veld")
plt.plot(time, (B + eddy) * c, "--", color="tab:orange", label="Veld incl. Eddy currents")
plt.title("Kalibratiemeting met gemodelleerde Eddy currents")
plt.xlabel("Tijd $(ms)$")
plt.ylabel("Magnetische veldsterkte $(mT)$")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("modelled_eddy_field.png", dpi=150)
plt.close()

# Plot 2: model vs measured residual
mask = (time >= 15.0) & (time <= 22.0)
plt.figure(figsize=(8, 4))
plt.plot(time[mask], residual[mask] / k, color="tab:orange", label="Gemeten residu")
plt.plot(time[mask], eddy[mask] / k, color="tab:blue", label="Gemodelleerde Eddy currents")
plt.title("Gemodelleerd en gemeten Eddy current residu (5 mm staal)")
plt.xlabel("Tijd $(ms)$")
plt.ylabel("Magnetische veldsterkte $(a.u.)$")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("modelled_and_experimental_eddy_currents.png", dpi=150)
plt.close()