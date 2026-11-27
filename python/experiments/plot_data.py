import matplotlib.pyplot as plt

from core import pect

processors = []

for i in range(10):
    df = pect.read_mst(f"deviation_tests/sample_1/t5mm_{i + 1}.csv")
    processor = pect.DataProcessor(df)
    processors.append(processor)

for processor in processors:
    pect.plot_signal(processor)

plt.grid(True)
plt.xlabel("Tijd $(ms)$")
plt.ylabel("Signaal $(mT)$")
plt.show()
