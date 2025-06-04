# Fractional-Order Leaky Integrate-and-Fire (FoLIF) Neuron Benchmarking

This repository contains the SPICE netlist and Python scripts for comprehensive benchmarking of a hardware-oriented Fractional-Order Leaky Integrate-and-Fire (FoLIF) neuron.

The neuron implementation utilizes a Biolek Memcapacitor model to achieve fractional-order dynamics, combined with a Schmitt trigger for spike detection and reset.

## Project Structure:

- `0_project_setup/`: Contains initial setup files and the base SPICE netlist template.
- `1_spice_data_processing/`: Scripts for parsing and analyzing raw SPICE output data.
- `2_throughput_max_freq_benchmarks/`: Scripts and notes for throughput and maximum operating frequency characterization.
- `3_adc_dac_benchmarks/`: Scripts and notes for analog-to-spike and spike-to-analog encoding/decoding characteristics.
- `4_operating_characteristics/`: Scripts and notes for power consumption, subthreshold dynamics, and reset behavior.
- `5_variability_robustness/`: Scripts and notes for Monte Carlo simulations and parameter sensitivity analysis (advanced).
- `results/`: Directory to store all generated plots, tables, and processed data.

## Neuron Model Overview:

- **Type:** Leaky Integrate-and-Fire (LIF)
- **Fractional Order:** Implemented via a Biolek Memcapacitor.
- **Spike Mechanism:** Schmitt Trigger-based threshold detection and MOSFET-based reset.
- **Simulator:** ngspice

## Benchmarking Goals:

- Throughput (spiking rate vs. input current)
- Maximum Operating Frequency
- Analog-to-Digital Conversion (ADC-like) capabilities
- Power Consumption (Energy per Spike)
- Subthreshold dynamics and Fractional Order impact
- Reset characteristics
- Robustness to parameter variations (if applicable)

