import pect
import matplotlib.pyplot as plt

data = pect.Data("calibration.csv")

pect.plot_data(data, normalize=False)

plt.show()