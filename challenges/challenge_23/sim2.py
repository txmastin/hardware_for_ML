import numpy as np
import matplotlib.pyplot as plt

class FractionalLIF:
    def __init__(self, Iin_amp=2e-6, Rleak=500e3, Vth=0.5, Ireset=50e-6,
                 Rs=[1.19e9, 2.12e9, 3.76e9], Cs=[0.75e-9, 13.3e-9, 237e-9],
                 dt=1e-5, T=0.05):
        self.Iin_amp = Iin_amp
        self.Rleak = Rleak
        self.Vth = Vth
        self.Ireset = Ireset
        self.Rs = Rs
        self.Cs = Cs
        self.dt = dt
        self.T = T
        self.steps = int(T/dt)

    def run(self):
        vmem = 0.0
        Vs = np.zeros(len(self.Rs))
        t = np.linspace(0, self.T, self.steps)
        Vmem = np.zeros(self.steps)
        Spikes = np.zeros(self.steps)

        for i in range(self.steps):
            Iin = self.Iin_amp
            # Capacitive ladder currents
            Icap = sum((Vs[j-1] - Vs[j]) / self.Rs[j] if j>0 else (vmem - Vs[j]) / self.Rs[j]
                       for j in range(len(self.Rs)))
            Ir = sum(Vs[j] / self.Rs[j] for j in range(len(self.Rs)))

            dv = (Iin - vmem/self.Rleak - Icap + Ir) * self.dt / self.Cs[0]
            vmem += dv

            # Update ladder nodes
            for j in range(len(self.Rs)):
                prev = vmem if j==0 else Vs[j-1]
                dVj = ((prev - Vs[j]) / self.Rs[j] - Vs[j]/self.Rs[j]) * (self.dt / self.Cs[j])
                Vs[j] += dVj

            if vmem >= self.Vth:
                Spikes[i] = 1
                vmem -= self.Ireset * self.Rleak

            Vmem[i] = vmem

        return t, Vmem, Spikes

# Run and plot
neuron = FractionalLIF()
t, Vmem, Spikes = neuron.run()

plt.figure(figsize=(8,4))
plt.plot(t, Vmem, label='V_membrane')
plt.step(t, Spikes * neuron.Vth, where='post', label='Spike')
plt.xlabel('Time (s)')
plt.ylabel('Voltage (V)')
plt.title('Fractional LIF Neuron Simulation')
plt.legend()
plt.show()

