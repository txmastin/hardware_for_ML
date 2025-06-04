# Phase 2: Throughput and Maximum Operating Frequency Benchmarking

This phase focuses on characterizing the fundamental dynamic response of the FoLIF neuron: how its firing rate changes with varying input current. This generates the crucial **I-F (Current-to-Frequency) curve** and helps determine the neuron's **maximum operating frequency (throughput)**.

## Key Concepts:

-   **I-F Curve:** A plot showing the neuron's output firing rate (Hz) as a function of the constant input current (Amps or µA). This curve reveals the neuron's threshold current, its sensitivity to input, and its maximum firing rate.
-   **Throughput / Maximum Operating Frequency:** The highest sustainable firing rate the neuron can achieve. This is a critical metric for estimating the processing speed of a neuromorphic chip.
-   **Energy per Spike:** By combining power measurements (from `Iin` and `Mreset`) with the firing rate, we can calculate the energy consumed per spike, a vital efficiency metric for hardware.

## Contents:

-   `run_if_benchmark.py`: Python script to automate ngspice simulations across a range of input currents, collect output data, and plot the I-F curve and Energy/Spike curve.
-   `results/`: Subdirectory to store generated plots and CSV data from this benchmark.
-   `README.md`: This file, detailing the steps.

## Key Steps:

1.  Create the `run_if_benchmark.py` script.
2.  Implement logic within `run_if_benchmark.py` to:
    * Iterate through a predefined range of input currents.
    * For each current, modify the `neuron_template.cir` from `0_project_setup/`.
    * Execute ngspice to run the simulation.
    * Call `spice_analyzer.py` (from `1_spice_data_processing/`) to analyze the `output_data.txt`.
    * Store the extracted metrics.
3.  Generate and save the I-F curve and Energy/Spike curve plots.
4.  Analyze the results for neuron characteristics like threshold current and maximum firing rate.
