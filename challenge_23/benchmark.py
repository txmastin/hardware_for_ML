#!/usr/bin/env python3
import numpy as np
import time
import pandas as pd

def simulate_rc_ladder(T, dt, Iin_amp=2e-6, alpha=0.8, stages=5):
    n_steps = int(T/dt)
    C0 = 1e-9
    flow = 0.1
    freqh = 1e4
    PI = np.pi
    ratio = (freqh/flow)**(1/(stages-1))
    Rbase = 1/(2*PI*flow*C0*(ratio**((1-alpha)/2)))
    Cbase = C0*(ratio**((alpha-1)/2))
    Rs = [Rbase*(ratio**(i*(1-alpha))) for i in range(stages)]
    Cs = [Cbase*(ratio**i) for i in range(stages)]
    Rleak = 500e3

    v_mem = np.zeros(n_steps)
    v = np.zeros(stages)

    for i in range(n_steps):
        if i == 0:
            v_prev = v.copy()
            vm = 0.0
        else:
            v_prev = v.copy()
            vm = v_mem[i-1]

        # membrane update
        dvm = dt * (Iin_amp - vm/Rleak - (vm - v_prev[0])/Rs[0]) / C0
        v_mem[i] = vm + dvm

        # ladder updates
        for j in range(stages):
            vin = vm if j == 0 else v_prev[j-1]
            if j < stages - 1:
                vout = v_prev[j+1]
                flow_rate = (vin - v_prev[j]) / Rs[j] - (v_prev[j] - vout) / Rs[j+1]
            else:
                flow_rate = (vin - v_prev[j]) / Rs[j]
            v[j] = v_prev[j] + dt * flow_rate / Cs[j]

    return v_mem

def simulate_fractional(T, dt, order=0.8, Iin_amp=2e-6):
    n_steps = int(T/dt)
    # Grünwald–Letnikov weights
    w = np.zeros(n_steps)
    w[0] = 1.0
    for k in range(1, n_steps):
        w[k] = w[k-1] * ((order - (k-1)) / k)

    v = np.zeros(n_steps)
    for i in range(n_steps):
        v[i] = (dt**order) * Iin_amp * np.sum(w[:i+1])

    return v

def benchmark(fn, **kwargs):
    t0 = time.perf_counter()
    fn(**kwargs)
    return time.perf_counter() - t0

def main():
    # Parameters
    T        = 0.5       # total sim time (s)
    dt       = 1e-6       # timestep (s)
    stages   = 5          # ladder stages
    alpha    = 0.8        # ladder fractional order
    order    = 0.8        # fractional-deriv order
    Iin_amp  = 2e-6       # input current (A)
    f_clk    = 100e6      # target ASIC clock (Hz)

    # Run benchmarks
    t_ladder = benchmark(simulate_rc_ladder, T=T, dt=dt,
                         Iin_amp=Iin_amp, alpha=alpha, stages=stages)
    t_frac   = benchmark(simulate_fractional, T=T, dt=dt,
                         order=order, Iin_amp=Iin_amp)

    # Compute metrics
    steps              = int(T/dt)
    ops_ladder         = 2 * stages
    ops_frac           = 2 * steps
    dt_min_ladder      = ops_ladder / f_clk
    dt_min_frac        = ops_frac / f_clk
    throughput_ladder  = steps / t_ladder
    throughput_frac    = steps / t_frac

    # Tabulate and print
    df = pd.DataFrame({
        'Implementation':    ['RC-ladder',      'Frac-deriv'],
        'Python runtime (s)': [t_ladder,         t_frac],
        'Steps/sec':         [throughput_ladder, throughput_frac],
        'Ops/step':          [ops_ladder,        ops_frac],
        'Min Δt @100 MHz (s)': [dt_min_ladder,    dt_min_frac]
    })

    print('\nBenchmark comparison (T = {:.3f}s, dt = {:.1e}s):'.format(T, dt))
    print(df.to_string(index=False, float_format='{:,.3e}'.format))

if __name__ == '__main__':
    main()

