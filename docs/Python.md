# Python Module Summary

The `python/` directory contains the software stack for interacting with the PECT sensor, processing its measurements, and modeling the underlying physics.

## Core Components
- **`core/`**: The foundation of the project.
  - `pec_sensor.py`: Hardware abstraction layer for the PECT sensor, handling measurement commands and data parsing.
  - `pect.py`: Data processing pipeline for CSV measurements, including normalization, signal filtering, and residual analysis.
  - `protocol.py`: Low-level serial communication handling, including port discovery and threaded command execution.

## Analysis and Modeling
- **`analysis/`**: Scripts for data interpretation.
  - `exp_fft.py`: Tools for analyzing eddy current decay in the frequency domain.
  - `mst_fft.py`: Specific scripts for performing FFTs on MST measurement data.
  - `thickness_plot_msts.py`: Visualization tools for comparing residuals across different material thicknesses.
- **`models/`**: Physics-based simulations.
  - `model_eddy_currents.py`: Models the exponential decay of eddy current fields and provides fitting routines for experimental data.
  - `modelled_eddy_fft.py`: Visualizes the frequency domain of the modeled eddy current fields.

## User Interface
- **`ui/`**: Graphical user interfaces for sensor interaction.
  - `BaseUI_PECTsensor.py`: A Tkinter application for real-time sensor control and live data visualization.
  - `BaseUI_PECTsensor_csv.py`: An enhanced UI that adds CSV export capabilities for captured measurement data.
