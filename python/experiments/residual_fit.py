import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from core import pect

fit_start, fit_end = (15.1, 19.0)

def exp_fit(t, tau, k):
    return k * np.exp(-t / tau)


calibration_df = pect.read_mst("deviation_tests/sample_5/calibration.csv")
calibration = pect.DataProcessor(calibration_df)

taus = []

for i in range(10):
    df = pect.read_mst(f"deviation_tests/sample_5/t1mm_{i + 1}.csv")
    processor = pect.DataProcessor(df)

    mask = (processor.df["time_ms"] >= fit_start) & (processor.df["time_ms"] <= fit_end)

    t = processor.df["time_ms"][mask]
    y = processor.df["residuals"][mask]

    popt, pcov = curve_fit(exp_fit, t, y, p0=[2.0, 100.0], maxfev=10000)

    tau, k = popt
    taus.append(tau)

    if i+1 <= 1:
        ye = exp_fit(t, tau, k)
        plt.plot(t, y, label=f"tau: {tau:.2f}, k: {k:.2f}")
        plt.plot(t, ye, label=f"d5mm_{i+1}")



for i in range(len(taus)):
    tau = taus[i]
    print(f"measurement {i+1}:", round(tau, 3))

print("\n")
print("mean:", np.mean(taus))
print("standard deviation:", np.std(taus))

plt.grid(True)
plt.legend()
plt.show()
