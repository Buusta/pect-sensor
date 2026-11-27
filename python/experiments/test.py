import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from scipy import fft

from core import pect

measurement = pect.read_mst("measurement_8.csv")
data = pect.DataProcessor(measurement)

time = data.df["time_ms"].to_numpy()
signal = data.df["normalized"].to_numpy()

fig, (ax_time, ax_fft) = plt.subplots(2, 1, figsize=(11, 8))
plt.subplots_adjust(bottom=0.34, hspace=0.4)

# Time-domain plots
ax_time.plot(time, signal, alpha=0.3, label="Full original signal")
(line_original,) = ax_time.plot([], [], label="Selected original")
(line_filtered,) = ax_time.plot([], [], linewidth=2, label="IFFT filtered")
ax_time.set_xlabel("Time (ms)")
ax_time.set_ylabel("Magnetic field (mT)")
ax_time.grid(True)
ax_time.legend()

# Frequency-domain plot
(line_spectrum,) = ax_fft.plot([], [])
ax_fft.set_xlabel("Frequency (Hz)")
ax_fft.set_ylabel("Magnitude")
ax_fft.set_title("Filtered frequency spectrum")
ax_fft.grid(True)

# Time selection sliders
ax_tmin = plt.axes([0.2, 0.25, 0.65, 0.025])
ax_tmax = plt.axes([0.2, 0.21, 0.65, 0.025])

s_tmin = Slider(ax_tmin, "Start (ms)", time.min(), time.max(), valinit=time.min())
s_tmax = Slider(ax_tmax, "End (ms)", time.min(), time.max(), valinit=time.max())

# Frequency selection sliders
ax_fmin = plt.axes([0.2, 0.13, 0.65, 0.025])
ax_fmax = plt.axes([0.2, 0.09, 0.65, 0.025])

s_fmin = Slider(ax_fmin, "Min freq (Hz)", 0, 1, valinit=0)
s_fmax = Slider(ax_fmax, "Max freq (Hz)", 0, 1, valinit=1)


def update(_):
    t_start = s_tmin.val
    t_end = s_tmax.val

    if t_start >= t_end:
        return

    mask = (time >= t_start) & (time <= t_end)
    t = time[mask]
    y = signal[mask]

    if len(y) < 4:
        return

    # FFT of selected signal
    dt = np.mean(np.diff(t)) / 1000
    frequencies = fft.rfftfreq(len(y), d=dt)
    spectrum = fft.rfft(y)

    nyquist = frequencies[-1]

    # Keep frequency sliders within the current Nyquist range
    s_fmin.valmax = nyquist
    s_fmax.valmax = nyquist
    s_fmin.ax.set_xlim(0, nyquist)
    s_fmax.ax.set_xlim(0, nyquist)

    low = min(s_fmin.val, nyquist)
    high = min(s_fmax.val, nyquist)

    # Remove frequencies outside the selected band
    filtered_spectrum = spectrum.copy()
    filtered_spectrum[(frequencies < low) | (frequencies > high)] = 0

    # Inverse FFT reconstructs the filtered time-domain signal
    filtered_signal = fft.irfft(filtered_spectrum, n=len(y))

    line_original.set_data(t, y)
    line_filtered.set_data(t, filtered_signal)
    line_spectrum.set_data(frequencies, np.abs(filtered_spectrum))

    ax_time.relim()
    ax_time.autoscale_view(scalex=False, scaley=True)

    ax_fft.set_xlim(0, nyquist)
    ax_fft.relim()
    ax_fft.autoscale_view()

    fig.canvas.draw_idle()


for slider in (s_tmin, s_tmax, s_fmin, s_fmax):
    slider.on_changed(update)

update(None)
plt.show()
