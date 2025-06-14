import numpy as np
import matplotlib.pyplot as plt

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
        v_prev = v.copy()
        vm = v_mem[i-1] if i > 0 else 0.0

        # Update membrane voltage
        dvm = dt * (Iin_amp - vm/Rleak - (vm - v_prev[0])/Rs[0]) / C0
        v_mem[i] = vm + dvm

        # Update ladder nodes
        for j in range(stages):
            vin = vm if j == 0 else v_prev[j-1]
            if j < stages - 1:
                vout = v_prev[j+1]
                flow_rate = (vin - v_prev[j]) / Rs[j] - (v_prev[j] - vout) / Rs[j+1]
            else:
                flow_rate = (vin - v_prev[j]) / Rs[j]
            v[j] = v_prev[j] + dt * flow_rate / Cs[j]

    return v_mem

def simulate_GL(dt, T, Tmem, tref, Cm, gl, Vl, Vth, Vinit, Vreset, Vpeak, Iapp, alpha):
    import numpy as np
    n_steps = int(T / dt)
    if Tmem > 0:
        n_mem = int(Tmem / dt)
    else:
        n_mem = n_steps

    I_ext = Iapp * np.ones(n_steps)
    V = Vl * np.ones(n_steps)
    spikes = []

    # Compute Grünwald–Letnikov coefficients
    coeffs = np.ones(n_mem)
    for i in range(1, n_mem):
        coeffs[i] = coeffs[i-1] * (1 - (1+alpha)/i)
    coeffs = coeffs[1:]

    DeltaM = np.ones(len(coeffs)) * Vinit
    tprev_spike = 2 * tref
    t = np.linspace(0, T, n_steps)

    for i in range(1, n_steps):
        DeltaM = np.concatenate([[V[i-1]], DeltaM[:-1]])
        Mem_comp = np.dot(coeffs, DeltaM)

        if tprev_spike > tref:
            dV = (-gl * (V[i-1] - Vl) + I_ext[i]) / Cm
            V_new = (dt**alpha) * dV - Mem_comp
            if V_new >= Vth:
                V[i] = Vpeak
                spikes.append(t[i] - dt*(V_new - Vth)/(V_new - V[i-1]))
                tprev_spike = 0
            else:
                V[i] = V_new
        else:
            V[i] = Vreset

        tprev_spike += dt

    return V, None, np.array(spikes)

def compute_spike_rate(v, dt, Vth=0.5):
    crossings = np.where((v[:-1] < Vth) & (v[1:] >= Vth))[0]
    return len(crossings) / (len(v) * dt)

# Simulation parameters
T = 0.1       # total time (s)
dt = 1e-5     # timestep (s)
alpha = 0.8
stages = 5
# GL parameters
Tmem = 0    # use full history
tref = 0.005
Cm = 1e-9
gl = 1/500e3
Vl = 0
Vth = 0.5
Vinit = 0
Vreset = 0
Vpeak = 1

Iin_values = np.linspace(1e-6, 5e-6, 10)
rates_ladder, rates_gl = [], []

for Iin in Iin_values:
    # RC-ladder spike rate
    v_ladder = simulate_rc_ladder(T, dt, Iin_amp=Iin, alpha=alpha, stages=stages)
    rates_ladder.append(compute_spike_rate(v_ladder, dt))

    # GL-LIF spike rate
    V_gl, _, spikes = simulate_GL(dt, T, Tmem, tref, Cm, gl, Vl, Vth, Vinit, Vreset, Vpeak, Iin, alpha)
    rates_gl.append(len(spikes) / T)

# Plotting
plt.plot(Iin_values, rates_ladder, label='RC-ladder')
plt.plot(Iin_values, rates_gl, label='GL-LIF')
plt.xlabel('Input current (A)')
plt.ylabel('Spike rate (Hz)')
plt.title('Spike Rate vs Input Current')
plt.legend()
plt.show()

