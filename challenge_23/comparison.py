#!/usr/bin/env python3
import numpy as np
import pandas as pd

# Hardware parameters
f_clk_asic = 200e6   # ASIC clock frequency (Hz)
f_clk_cpu  = 3e9     # CPU core clock frequency (Hz)

# Model parameters
stages = 5           # number of RC-ladder stages
T      = 0.01        # total simulated time (s) for GL method
dt     = 1e-5        # simulation timestep (s)

# Compute number of steps for GL (full history)
steps   = int(T / dt)

# Operations per step
ops_ladder = 2 * (stages + 1)  # 2 ops per pole (stages + leak)
ops_gl     = 2 * steps         # 2 ops per memory element (full history)

# Compute minimum real-time timestep and max update rate
dt_min_ladder = ops_ladder / f_clk_asic
dt_min_gl     = ops_gl     / f_clk_cpu
f_max_ladder  = 1.0 / dt_min_ladder
f_max_gl      = 1.0 / dt_min_gl

# Create summary table
df = pd.DataFrame({
    'Implementation':       ['RC-ladder (ASIC)', 'GL-LIF (CPU)'],
    'Clock freq (Hz)':      [f_clk_asic, f_clk_cpu],
    'Ops/step':             [ops_ladder, ops_gl],
    'Min Δt (s)':           [dt_min_ladder, dt_min_gl],
    'Max real‑time rate (Hz)': [f_max_ladder, f_max_gl]
})

# Display results
print("ASIC vs CPU Performance Comparison\n")
print(df.to_string(index=False, float_format='%.3e'))

