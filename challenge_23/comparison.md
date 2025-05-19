# ASIC vs CPU Performance Comparison

## Overview

We compare two implementations:

- **RC-ladder (ASIC)**: Dedicated hardware component running at 200 MHz.
- **GL-LIF (CPU)**: Grünwald–Letnikov fractional LIF implemented on a 3 GHz CPU core.

## Performance Metrics

| Implementation      | Clock Frequency (Hz) | Operations per Step | Minimum Δt (s) | Maximum Real‑Time Rate (Hz) |
|---------------------|----------------------|---------------------|---------------:|----------------------------:|
| RC-ladder (ASIC)    | 2.00e8               | 12                  |       6.00e-08 |                   1.67e7    |
| GL-LIF (CPU)        | 3.00e9               | 998                 |       3.33e-07 |                   3.01e6    |

## Interpretation

- The **ASIC RC‑ladder** can advance neuron state every **60 ns**, supporting up to **16.7 MHz** real-time update rate.
- The **CPU GL‑LIF** can advance state every **333 ns**, supporting up to **3.0 MHz** real-time update rate.
- Thus, the ASIC implementation is approximately **5× faster**, making it more suitable for high-throughput neuromorphic applications.
