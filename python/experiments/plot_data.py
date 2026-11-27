import matplotlib.pyplot as plt

from core import pect

calibration_df = pect.read_mst("measurement_6.csv")
calibration = pect.DataProcessor(calibration_df)
# d2mm = pect.DataProcessor("distance_msts/d2mm.csv")
# d3mm = pect.DataProcessor("distance_msts/d3mm.csv")
# d4mm = pect.DataProcessor("distance_msts/d4mm.csv")
# d5mm = pect.DataProcessor("distance_msts/d5mm.csv")
# d6mm = pect.DataProcessor("distance_msts/d6mm.csv")
# d7mm = pect.DataProcessor("distance_msts/d7mm.csv")
# d8mm = pect.DataProcessor("distance_msts/d8mm.csv")
# d9mm = pect.DataProcessor("distance_msts/d9mm.csv")

# pect.plot_signal(calibration, normalize=False)
pect.plot_residuals(calibration, bin_n=20)
# pect.plot_signal(d2mm, normalize=True)
# # pect.plot_signal(d3mm, normalize=True)
# # pect.plot_signal(d4mm, normalize=True)
# pect.plot_signal(d5mm, normalize=True)
# pect.plot_signal(d6mm, normalize=True)
# # pect.plot_signal(d7mm, normalize=True)
# # pect.plot_signal(d8mm, normalize=True)
# pect.plot_signal(d9mm, normalize=True)


# mst.get_residuals(base)

# pect.plot_residuals(mst)

plt.grid(True)
plt.xlabel("Tijd $(ms)$")
plt.ylabel("Signaal $(mT)$")
plt.show()
