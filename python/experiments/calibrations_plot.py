import pect
import matplotlib.pyplot as plt

cal_1 = pect.Data("calibration_test/calibration_1.csv")
cal_2 = pect.Data("calibration_test/calibration_2.csv")
cal_3 = pect.Data("calibration_test/calibration_3.csv")
cal_4 = pect.Data("calibration_test/calibration_4.csv")
cal_5 = pect.Data("calibration_test/calibration_5.csv")
cal_6 = pect.Data("calibration_test/calibration_6.csv")
cal_7 = pect.Data("calibration_test/calibration_7.csv")
cal_8 = pect.Data("calibration_test/calibration_8.csv")
cal_9 = pect.Data("calibration_test/calibration_9.csv")
cal_10 = pect.Data("calibration_test/calibration_10.csv")

baseline = cal_1.df

res_2 = pect.residuals(baseline, cal_2.df)
res_3 = pect.residuals(baseline, cal_3.df)
res_4 = pect.residuals(baseline, cal_4.df)
res_5 = pect.residuals(baseline, cal_5.df)
res_6 = pect.residuals(baseline, cal_6.df)
res_7 = pect.residuals(baseline, cal_7.df)
res_8 = pect.residuals(baseline, cal_8.df)
res_9 = pect.residuals(baseline, cal_9.df)
res_10 = pect.residuals(baseline, cal_10.df)

from_peak = True

pect.plot_residuals(res_2, label="cal_2", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_3, label="cal_3", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_4, label="cal_4", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_5, label="cal_5", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_6, label="cal_6", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_7, label="cal_7", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_8, label="cal_8", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_9, label="cal_9", normalize=False, from_peak=from_peak)
pect.plot_residuals(res_10, label="cal_10", normalize=False, from_peak=from_peak)

plt.title("Normalized magnetic field residuals")
plt.xlabel("Time $(ms)$")
plt.ylabel("Normalized magnetic field $(a.u.)$")
plt.legend()
plt.grid(True)
plt.savefig("calibration_residuals.png", dpi=100)
plt.show()