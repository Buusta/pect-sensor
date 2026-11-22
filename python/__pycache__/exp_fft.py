import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as fft


def exp_decay(x, tau_ms, gain):
    decay = np.exp(-x / tau_ms) * gain
    return decay

def exp_fourier(w, tau_s):
    fourier = tau_s / (1.0 + 1j * w * tau_s)
    return fourier

tau_list = [0.5, 1.0, 2.0, 4.0, 8.0]
k = 1.0

t = np.arange(0.0, 25.0, 1.0 / 200)

for tau_ms in tau_list:
    y = exp_decay(t, tau_ms, k)
    plt.plot(t, y, label=f"tau: {tau_ms} ms")

plt.grid(True)
plt.xlabel("Tijd $(ms)$")
plt.ylabel("$(a.u)$ (genormalizeerd)")
plt.legend()
plt.show()
plt.clf()

f = np.linspace(0, 6000, 3000)
w = 2.0 * np.pi * f
for tau_ms in tau_list:
    tau_s = tau_ms * 1e-3
    yf = exp_fourier(w, tau_s)
    plt.plot(f, np.abs(yf) / tau_s, label=f"tau: {tau_ms} ms")


plt.grid(True)
plt.xlabel("Frequentie $(Hz)$")
plt.ylabel("$(a.u)$ (genormalizeerd)")
plt.legend()
plt.show()
