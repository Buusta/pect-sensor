import pect
import matplotlib.pyplot as plt

cal = pect.Data("distance_msts_2/calibration.csv")
d2mm = pect.Data("distance_msts_2/d2mm.csv")
d3mm = pect.Data("distance_msts_2/d3mm.csv")
d4mm = pect.Data("distance_msts_2/d4mm.csv")
d5mm = pect.Data("distance_msts_2/d5mm.csv")
d6mm = pect.Data("distance_msts_2/d6mm.csv")
d7mm = pect.Data("distance_msts_2/d7mm.csv")
d8mm = pect.Data("distance_msts_2/d8mm.csv")
d9mm = pect.Data("distance_msts_2/d9mm.csv")

res_d2mm = pect.residuals(cal.df, d2mm.df)
res_d3mm = pect.residuals(cal.df, d3mm.df)
res_d4mm = pect.residuals(cal.df, d4mm.df)
res_d5mm = pect.residuals(cal.df, d5mm.df)
res_d6mm = pect.residuals(cal.df, d6mm.df)
res_d7mm = pect.residuals(cal.df, d7mm.df)
res_d8mm = pect.residuals(cal.df, d8mm.df)
res_d9mm = pect.residuals(cal.df, d9mm.df)

pect.plot_residuals(res_d2mm, label="dist=2mm")
# pect.plot_residuals(res_d3mm, label="dist=3mm")
pect.plot_residuals(res_d4mm, label="dist=4mm")
# pect.plot_residuals(res_d5mm, label="dist=5mm")
# pect.plot_residuals(res_d6mm, label="dist=6mm")
pect.plot_residuals(res_d7mm, label="dist=7mm")
# pect.plot_residuals(res_d8mm, label="dist=8mm")
pect.plot_residuals(res_d9mm, label="dist=9mm")


plt.title("Normalized magnetic field residuals")
plt.xlabel("Time $(ms)$")
plt.ylabel("Normalized magnetic field $(a.u.)$")
plt.legend()
plt.grid(True)
plt.savefig("distance_residuals.png", dpi=100)
plt.show()