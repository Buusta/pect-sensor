import pect
import matplotlib.pyplot as plt

base = pect.DataProcessor("calibration.csv")
mst = pect.DataProcessor("capture.csv")

pect.plot_signal(base, normalize=True)
pect.plot_signal(mst, normalize=True)

# mst.get_residuals(base)

# pect.plot_residuals(mst)

plt.show()
