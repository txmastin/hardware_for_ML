## Binary LIF Neuron

The Binary Leaky Integrate-and-Fire (LIF) neuron is a simplified spiking model where the neuron's output is binary (`0` = not spiking, `1` = spiking). It integrates input over time, applies a leak factor to the internal potential, and emits a spike when the potential crosses a threshold.

### State Representation
- `S(t) ∈ {0, 1}` — the neuron's output at time `t` (spike = `1`, otherwise `0`)
- `P(t)` — the internal potential (integer-valued)

---

### Update Rules

1. **Leak and Accumulate**
   - The potential decays over time according to a leak factor `λ = LEAK_NUM / LEAK_DEN`:
     ```
     P(t) = λ · P(t−1) + I(t)
     ```
   - `I(t) ∈ {0, 1}` is the binary input at time `t`

2. **Threshold and Spike**
   - If `P(t) ≥ θ`, the neuron spikes:
     ```
     S(t) = 1
     P(t) ← RESET_VAL
     ```
   - Otherwise:
     ```
     S(t) = 0
     ```

---

### Parameters
- `THRESHOLD` — the spike threshold value (θ)
- `RESET_VAL` — the potential value after spiking (typically 0)
- `LEAK_NUM` / `LEAK_DEN` — numerator and denominator defining the leak factor λ (`0 < λ < 1`)

---

### Verilog Implementation
- The neuron is implemented as a synchronous module with:
  - One binary input (`in`)
  - One binary output (`spike`)
  - Internal integer-valued potential (`potential`)
- All logic is updated on the rising edge of the clock
- The module uses integer arithmetic and saturates behavior by design

---

### Testbench Scenarios
1. **Constant input below threshold**  
   Input stays at `0`, potential remains at `0`, no spikes occur

2. **Input that accumulates until reaching threshold**  
   Repeated `1` inputs raise potential until it spikes, then resets

3. **Leakage with no input**  
   After receiving input, input drops to `0` and potential decays over time

4. **Strong input causing immediate spike**  
   Potential is manually preloaded just below threshold; a single input triggers a spike

---

### Output of Testbench:

```
--- Scenario 1: Constant input below threshold ---


Time    In        V     Spike
15      0         0     0
25      0         0     0
35      0         0     0
45      0         0     0
55      0         0     0
65      0         0     0
75      0         0     0
85      0         0     0
95      0         0     0
105     0         0     0

--- Scenario 2: Accumulating input until spike ---


Time    In        V     Spike
115     1         1     0
125     1         2     0
135     1         3     0
145     1         4     0
155     1         5     0
165     1         0     1

--- Scenario 3: Leakage with no input ---


Time    In        V     Spike
175     1         1     0
185     1         2     0
195     1         3     0
205     0         2     0
215     0         1     0
225     0         0     0
235     0         0     0
245     0         0     0
255     0         0     0
265     0         0     0
275     0         0     0
285     0         0     0
295     0         0     0

--- Scenario 4: Strong input causing immediate spike ---


Time    In        V     Spike
305     1         5     1

```

