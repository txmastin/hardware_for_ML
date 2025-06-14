import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
dt = 1e-3  # time step
T = 2      # total time in seconds
t = np.arange(0, T, dt)

# Input: sinusoidal voltage sweep
v_in = 5.0 * np.sin(2 * np.pi * 1 * t)  # 1 Hz sine wave

# Memristor parameters
R_on = 100.0       # Low resistance state
R_off = 16000.0    # High resistance state
D = 10e-9          # Thickness of memristor
mu_v = 1e-7       # Mobility of dopants

# Initialize state
w = 0.5 * D        # Initial doped region width
w_history = []
i_out = []

# Simulate memristor dynamics
for v in v_in:
    R = R_on * (w / D) + R_off * (1 - w / D)  # Total resistance
    i = v / R
    dw = mu_v * R_on * i * dt                # Rate of change of w
    w += dw
    w = np.clip(w, 0, D)                     # Ensure physical bounds
    w_history.append(w)
    i_out.append(i)

# Plot I-V hysteresis
plt.figure(figsize=(6, 5))
plt.plot(v_in, i_out, color='blue')
plt.title("Memristor I-V Hysteresis Curve")
plt.xlabel("Voltage (V)")
plt.ylabel("Current (A)")
plt.grid(True)
plt.show()

