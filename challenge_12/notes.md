# Overview

This project implements a basic 64-neuron spiking liquid state machine (LSM) in PyMTL3.The goal is to create a spiking reservoir with online-trainable output weights and evaluate it on time series prediction using the Mackey-Glass dataset.

The project is organized into four main parts:

Neuron.py — Defines the basic neuron behavior.

SpikingLSM64.py — Builds the full spiking network.

test_spiking_lsm_mg.py — Runs the LSM on Mackey-Glass prediction.

sim_test.py — Provides a simple sanity check test.

## Inputs:

in_spike_sum: Synaptic input sum.

in_input: External direct input.

Outputs:

fire_out: Spike output (binary).

v_mem_out: Current membrane potential.

## Overview of network:

Random sparse recurrent connections (w_flat), normalized to a spectral radius near 0.9.

Random external input weights (W_in).

Output weights (W_out_regs) that are trained online.

## Main logic blocks:

compute_inputs: Calculates neuron inputs from spikes and external signals.

update_spikes: Updates neuron firing states.

compute_output: Aggregates reservoir activity to make a prediction.

update_weights: Updates the readout layer using a simple learning rule.

## test_spiking_lsm_mg.py

Loads Mackey-Glass time series data.

Feeds inputs into the LSM and trains the readout layer on-the-fly.

Prints timestep, input, target, prediction, and error.


## Current Status

The project structure is mostly complete, but the system does not function yet. Efforts to debug with chatGPT were essentially useless, it kept going in circles. I think I'll have to manually work it out myself.
