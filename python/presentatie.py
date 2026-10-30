import pect
import matplotlib.pyplot as plt

calibratie = pect.Data("presentatie/calibratie.csv")
d5mm = pect.Data("presentatie/d5mm.csv")
d5mm_a6mm = pect.Data("presentatie/d5mm_a6mm.csv")

# pect.plot_data(calibratie)
# pect.plot_data(d5mm)

res_d5mm = pect.residuals(calibratie.df, d5mm.df)
res_d5mm_a6mm = pect.residuals(calibratie.df, d5mm_a6mm.df)

pect.plot_residuals(res_d5mm)
pect.plot_residuals(res_d5mm_a6mm)

plt.grid(True)
plt.title("Magnetisch veld sterkte, tijd")
plt.xlabel("Tijd $(ms)$")
plt.ylabel("Magnetisch veld sterkte $(mT)$")
plt.show()