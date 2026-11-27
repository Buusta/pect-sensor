import matplotlib.pyplot as plt
import numpy as np


def eddy_decay(t_ms, tau_ms):
    """Normalized exponential decay of the eddy current signal.

    Parameters
    ----------
    t_ms : array-like
        Time in ms.
    tau_ms : float
        Decay time constant in ms.

    Returns
    -------
    np.ndarray
        exp(-t / tau) normalized so its maximum value is 1.
    """
    t = np.asarray(t_ms, dtype=float)
    decay = np.exp(-t / tau_ms)
    return decay / decay.max()


def analytic_spectrum(f_hz, tau_ms):
    """Continuous-time Fourier transform of the causal decay e^{-t/tau} u(t).

    X(f) = int_0^inf exp(-t/tau) * exp(-i 2 pi f t) dt
         = tau / (1 + i 2 pi f tau)

    Parameters
    ----------
    f_hz : array-like
        Frequency in Hz.
    tau_ms : float
        Decay time constant in ms.

    Returns
    -------
    np.ndarray
        Complex spectrum X(f). Use np.abs() for magnitude, np.angle() for phase.
    """
    tau_s = tau_ms * 1e-3
    return tau_s / (1.0 + 2j * np.pi * f_hz * tau_s)


def normalize(spectrum):
    """Scale a spectrum so its maximum magnitude is 1 (arbitrary units)."""
    mag = np.abs(spectrum)
    return mag / mag.max()


# --- parameters -----------------------------------------------------------
t_ms = np.linspace(0.0, 20.0, 4000)  # 20 ms window @ 200 kHz
tau_ms_values = [0.5, 1.0, 2.0, 4.0]
f_max_hz = 5e3
f_analytic = np.linspace(0.0, f_max_hz, 2000)  # linear in Hz


# --- figure 1: time domain -------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4))
for tau in tau_ms_values:
    ax.plot(t_ms, eddy_decay(t_ms, tau), label=f"tau = {tau} ms")
ax.set_xlabel("Tijd $(ms)$")
ax.set_ylabel("Veldsterkte $(a.u.)$")
ax.set_title("Eddy current Decay")
ax.legend()
ax.grid(True)
fig.tight_layout()
fig.savefig("exp_decay.png", dpi=150)
plt.show()


# --- figure 2: frequency domain --------------------------------------------
f_c = {tau: 1.0 / (2 * np.pi * tau * 1e-3) for tau in tau_ms_values}

fig, ax = plt.subplots(figsize=(8, 4))
for tau in tau_ms_values:
    ax.plot(
        f_analytic,
        normalize(analytic_spectrum(f_analytic, tau)),
        label=f"tau = {tau} ms",
    )
    ax.axvline(f_c[tau], color="gray", lw=0.5, ls=":")

ax.set_xlabel("Frequentie $(Hz)$")
ax.set_ylabel("Amplitude $(a.u.)$")
ax.set_title("Eddy Decay Fourier transform")
ax.legend()
ax.grid(True)
fig.tight_layout()
fig.savefig("exp_fft.png", dpi=150)
plt.show()
