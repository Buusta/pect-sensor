import matplotlib.pyplot as plt
import pect

calibration = pect.DataProcessor("new_mst.csv")
# d2mm = pect.DataProcessor("distance_msts/d2mm.csv")
# d3mm = pect.DataProcessor("distance_msts/d3mm.csv")
# d4mm = pect.DataProcessor("distance_msts/d4mm.csv")
# d5mm = pect.DataProcessor("distance_msts/d5mm.csv")
# d6mm = pect.DataProcessor("distance_msts/d6mm.csv")
# d7mm = pect.DataProcessor("distance_msts/d7mm.csv")
# d8mm = pect.DataProcessor("distance_msts/d8mm.csv")
# d9mm = pect.DataProcessor("distance_msts/d9mm.csv")

pect.plot_signal(calibration, normalize=False)
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
plt.show()
