import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from core import pect


def exp_fit(t, tau, k):
    return k * np.exp(-t / tau)


calibration_df = pect.read_mst("deviation_tests/sample_1/calibration.csv")
calibration = pect.DataProcessor(calibration_df)

taus = []

for i in range(10):
    df = pect.read_mst(f"deviation_tests/sample_1/t5mm_{i + 1}.csv")
    processor = pect.DataProcessor(df)

    mask = (processor.df["time_ms"] >= 15.35) & (processor.df["time_ms"] <= 25.0)

    t = processor.df["time_ms"][mask]
    y = processor.df["residuals"][mask]

    popt, pcov = curve_fit(exp_fit, t, y, p0=[2.0, 100.0], maxfev=10000)

    tau, k = popt
    taus.append(tau)

    if i+1 <= 2:
        ye = exp_fit(t, tau, k)
        plt.plot(t, y - ye, label=f"tau: {tau:.2f}, k: {k:.2f}")
        # plt.plot(t, , label=f"d5mm_{i+1}")

print(np.std(taus))
print(np.mean(taus))

for tau in taus:
    print(round(tau, 3))

plt.grid(True)
plt.legend()
plt.show()
