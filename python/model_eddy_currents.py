import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pect

gradient_amplitude: float = 10.0
tau_ms: float = 2.0
eddy_gain: float = 0.05

calibration = pect.Data("calibration.csv")

time = calibration.df["time_ms"].to_numpy()
B = calibration.df["mT"].to_numpy()

# Eddy-current magnetic field (mT, a.u.)
eddy = np.zeros_like(B, dtype=float)

for i in range(1, len(time)):
    dt = time[i] - time[i - 1]
    decay = np.exp(-dt / tau_ms)
    dB = B[i] - B[i - 1]
    eddy[i] = eddy[i - 1] * decay - eddy_gain * dB

calibration.df["coil_field_mT"] = B
calibration.df["eddy_field"] = eddy
calibration.df["total_field"] = B + eddy

plt.figure(figsize=(8, 4))
plt.plot(time, B, label="Kalibratie veld")
plt.plot(time, eddy, label="Gemoddelleerde Eddy-current veld", color="tab:green")
plt.plot(time, B + eddy, "--", label="Totale veld", color="tab:orange")
plt.title("Kalibratiemeting met gemodelleerde Eddy-currents")
plt.xlabel("Tijd $(ms)$")
plt.ylabel("Magnetische veldsterkte $(mT)$")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("modelled_eddy_field.png", dpi=150)
#plt.show()
