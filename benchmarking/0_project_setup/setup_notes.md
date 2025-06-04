# Phase 0: Project Setup and Initial Files

This phase focuses on setting up the fundamental project structure and preparing the core SPICE netlist for automated parameter sweeping.

## Contents:

- `base_neuron.cir`: The original, unmodified SPICE netlist for reference.
- `neuron_template.cir`: A modified version of `base_neuron.cir` where key simulation parameters are replaced with placeholders (`{PARAM_NAME}`). This template will be used by Python scripts to generate specific netlists for each simulation run.
- `setup_notes.md`: This markdown file itself, detailing the steps.

## Key Steps:

1.  Copy original SPICE netlist to `base_neuron.cir`.
2.  Create `neuron_template.cir` by modifying `base_neuron.cir` to include placeholders for parameters that will be varied during benchmarking (e.g., input current, simulation time, memcapacitor parameters).
3.  Ensure ngspice is installed, up-to-date, and accessible.
