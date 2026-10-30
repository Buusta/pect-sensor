import pect
import matplotlib.pyplot as plt

cal_before = pect.Data("thickness_msts_2/calibration.csv")
cal_after = pect.Data("thickness_msts_2/capture.csv")
t1mm = pect.Data("thickness_msts_2/t1mm.csv")
t1_5mm = pect.Data("thickness_msts_2/t1_5mm.csv")
t3mm = pect.Data("thickness_msts_2/t3mm.csv")
t5mm = pect.Data("thickness_msts_2/t5mm.csv")

res_t1mm = pect.residuals(cal_after.df, t1mm.df)
res_t1_5mm = pect.residuals(cal_after.df, t1_5mm.df)
res_t3mm = pect.residuals(cal_after.df, t3mm.df)
res_t5mm = pect.residuals(cal_after.df, t5mm.df)
res_cals = pect.residuals(cal_after.df, cal_before.df)

pect.plot_residuals(res_t1mm, label="thickness=1mm")
pect.plot_residuals(res_t1_5mm, label="thickness=1.5mm")
pect.plot_residuals(res_t3mm, label="thickness=3mm")
pect.plot_residuals(res_t5mm, label="thickness=5mm")

plt.title("Normalized magnetic field residuals")
plt.xlabel("Time $(ms)$")
plt.ylabel("Normalized magnetic field $(a.u.)$")
plt.legend()
plt.grid(True)
plt.savefig("residuals.png", dpi=100)
plt.show()