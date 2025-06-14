import numpy as np
import matplotlib.pyplot as plt

# ---- parameters ----
alpha   = 0.8      # fractional order
stages  = 5        # RC‐ladder stages
C0      = 1e-9     # base capacitance
flow    = 0.1
freqh   = 1e4
ratio   = (freqh/flow)**(1/(stages-1))
R1      = 1/(2*np.pi*flow*C0*(ratio**((1-alpha)/2)))
C1      = C0*(ratio**((alpha-1)/2))

# build ladder elements
Rs = [R1*(ratio**(i*(1-alpha))) for i in range(stages)]
Cs = [C1*(ratio**i) for i in range(stages)]

print(Rs)

Iin_amp = 2e-6     # 2 µA
Rleak   = 500e3    # 500 kΩ
Vth     = 0.5      # V
Ireset  = 50e-6    # 50 µA
dt      = 1e-5     # 10 µs
Tstop   = 0.01      # 10 ms

# state variables
vmem = 0.0
Vs = [0.0]*stages  # ladder node voltages
tsteps = int(Tstop/dt)
t = np.linspace(0, Tstop, tsteps)
Vmem_trace = np.zeros_like(t)
Spike = np.zeros_like(t)

for i, ti in enumerate(t):
    # input current
    Iin = Iin_amp
    
    # ladder: compute ladder current back to membrane
    # simple nodal RC: combine all branch currents from vmem
    Icap = sum( Cs[j]*( (0 if j==0 else Vs[j-1]) - Vs[j] )/dt for j in range(stages) )
    Ir    = sum( Vs[j]/Rs[j] for j in range(stages) )
    # membrane update
    dv = ( Iin - vmem/Rleak - Icap + Ir ) / C0
    vmem += dv * dt
    
    # ladder updates
    Vin = vmem
    for j in range(stages):
        # current into Cj = (Vj-1 - Vj)/Rj  minus Vj/Cj
        prev = Vin if j==0 else Vs[j-1]
        dVj = ( (prev - Vs[j])/Rs[j] - Vs[j]/(Rs[j]*alpha) ) / Cs[j] * dt
        Vs[j] += dVj
    
    # spike?
    if vmem >= Vth:
        Spike[i]     = 1.0
        vmem        -= Ireset * Rleak  # simple reset
    Vmem_trace[i] = vmem

# plot
plt.figure(figsize=(8,4))
plt.plot(t, Vmem_trace, label='Vmem')
plt.plot(t, Spike, label='Spike (scaled)')
plt.xlabel('Time (s)')
plt.legend()
plt.show()

