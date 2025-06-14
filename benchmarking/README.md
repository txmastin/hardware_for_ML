# Fractional-Order Leaky Integrate-and-Fire (FoLIF) Neuron Benchmarking

This repository contains the SPICE netlist and Python scripts for comprehensive benchmarking of a hardware-oriented Fractional-Order Leaky Integrate-and-Fire (FoLIF) neuron.

The neuron implementation utilizes a Biolek Memcapacitor model to achieve fractional-order dynamics, combined with a Schmitt trigger for spike detection and reset.

## Benchmark Structure:

- `0_project_setup/`: Contains initial setup files and the base SPICE netlist template.
- `1_spice_data_processing/`: Scripts for parsing and analyzing raw SPICE output data.
- `2_throughput_max_freq_benchmarks/`: Scripts and notes for throughput and maximum operating frequency characterization.
- `3_comparison_to_python/`: Scripts and notes for comparison to a Python implementation emulating fractional-order neurons for a control task.
- `results/`: Directory to store all generated plots

## Neuron Model Overview:

- **Type:** Leaky Integrate-and-Fire (LIF)
- **Fractional Order:** Implemented via a Biolek Memcapacitor.
- **Spike Mechanism:** Schmitt Trigger-based threshold detection and MOSFET-based reset.
- **Simulator:** ngspice

## Benchmarking Goals:

- Throughput (spiking rate vs. input current)
- Maximum Operating Frequency
- Performance comparison to Python emulation
