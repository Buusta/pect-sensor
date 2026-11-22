import matplotlib.pyplot as plt
import numpy as np
import pect
import scipy.fft as fft

processor = pect.DataProcessor("new_mst.csv")

time_mask = (processor.df["time_ms"] >= 15.5) & (processor.df["time_ms"] <= 30.0)
t = processor.df["time_ms"][time_mask].to_numpy()
y = processor.df["normalized"][time_mask].to_numpy()

plt.plot(t, y)
plt.show()

dt = np.mean(np.diff(t)) * 1e-3
N = len(t)

win = np.hanning(N)
yf = fft.rfft(y)
f = fft.rfftfreq(N, dt)

plt.plot(f[1:], np.abs(yf[1:]))
plt.xlabel("Frequentie $(Hz)$")
plt.ylabel("Amplitude $(a.u.)$")
plt.grid(True)
plt.savefig("signal_f.png")
plt.show()

P = np.abs(yf)**2
P[0] = 0
cum = np.cumsum(P) / P.sum()

plt.plot(f[1:], cum[1:])
plt.xlabel("Frequentie $(Hz)$")
plt.ylabel("Energie $(a.u.)$")
plt.grid(True)
plt.savefig("signal_f_p.png")
plt.show()
