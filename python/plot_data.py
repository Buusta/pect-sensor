import pect
import matplotlib.pyplot as plt

base = pect.DataProcessor("distance_msts_2/calibration.csv")
mst = pect.DataProcessor("distance_msts_2/d7mm.csv")

# pect.plot_signal(base, normalize=False)
# pect.plot_signal(mst, normalize=False)

mst.get_residuals(base)

pect.plot_residuals(mst)

plt.show()
