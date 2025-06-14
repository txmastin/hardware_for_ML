# Hardware Spiking Fractional Leaky Integrate-and-Fire (fLIF) Neuron

## Key Features of the Circuit

* **Fractional-Order Dynamics:** Achieved via a Biolek memcapacitor model, imparting inherent history-dependence and non-local memory.
* **Internal Spike Rate Adaptation:** Designed to exhibit upward spike rate adaptation (facilitation), a complex dynamic less common than standard downward adaptation.
* **Analog Implementation:** Operates in continuous time, offering potential for ultra-low power consumption and natural processing of analog signals.
* **Robust Spiking:** Utilizes an explicit Op-Amp based Schmitt Trigger for clean, reliable spike generation.
* **Benchtop Compatible:** Can be physically built and tested without requiring expensive and time-consuming custom silicon fabrication.
* **High Performance:** Benchmarked for a maximum operating frequency of up to 72 kHz.
* **Low Neuron Count Efficiency:** Designed for applications where the rich dynamics of fLIF neurons enable complex tasks with very few computational units.

## Circuit Description

The neuron circuit is an analog implementation of an fLIF model, comprising several interconnected functional blocks: an input/leakage stage, a memcapacitive integrator, a Schmitt trigger for spiking, and a MOSFET-based reset mechanism.

### 1. The Memcapacitive Core (Fractional Order & History Dependence)

The memcapacitive model utilized in the analog neuron is implemented with the **Biolek Memcapacitor Model**. This component is critical for realizing the fractional-order dynamics and the neuron's inherent history dependence. Unlike standard capacitors, the memcapacitor's capacitance is not constant but depends on its past charge history, providing a physical embodiment of memory.

* **Netlist Instance:** `Xmemcap Vm 0 memC ...`
* **Parameters (from .param section):**
    * `MC_Cmin`: 10nF (Minimum capacitance)
    * `MC_Cmax`: 1000uF (Maximum capacitance)
    * `MC_Cinit`: 200nF (Initial capacitance)
    * `MC_k`: 10e6 (Memcapacitor model parameter)
    * `MC_p`: 1 (Memcapacitor model parameter for window function)
    * `MC_IC`: 0 (Initial charge offset)

**Biolek Memcapacitor Subcircuit (`.SUBCKT memC`):**
This subcircuit mathematically models the memcapacitor.
* `Emc`: A voltage-controlled voltage source (VCVS) that represents the voltage across the memcapacitor, dependent on an internal state variable `x` and the internal `charge` node. The `DM(x)` function defines how capacitance (inverse) changes with state `x`.
* `Gq` & `Cq`: An integral of the current `I(Emc)` through `Cq` effectively calculates the charge accumulated.
* `Gx` & `Cx`: Another integral (`v(charge) * k * window(v(x),p)`) that updates the internal state `x` based on charge and the window function. The `window(x,p)` function ensures state `x` remains within bounds (0 to 1). The initial condition `IC` for `Cx` is crucial for setting the starting state of the memcapacitor.

### 2. Input & Leakage Core

The fundamental leaky integrate-and-fire behavior is established here:

* **Input Current (`Iin`):** `Iin 0 Vm DC {I_CONST_IN}`
    * A constant DC current source injects charge onto the `Vm` node, simulating synaptic input that builds up the neuron's membrane potential.
* **Leak Resistance (`Rleak`):** `Rleak Vm 0 {R_LK}`
    * A parallel resistor `R_LK` (10k Ohms) allows charge to slowly leak from the `Vm` node towards ground (0V), mimicking the membrane leakage of a biological neuron and causing the potential to decay if input current ceases.

### 3. The Schmitt Trigger (Spiking Mechanism)

This block provides the robust, hysteresis-driven thresholding necessary for clean spike generation, preventing "chattering" from noisy input.

* **Op-Amp Core (`B_OPAMP_CORE`):** `B_OPAMP_CORE Vcomp_out_internal 0 V = min({VCC_OPAMP}, max({VEE_OPAMP}, {OPAMP_GAIN_CORE}*(V(Vplus_opamp_node) - V(V_REF_SCHMITT_NODE))))`
    * A behavioral voltage source models an ideal high-gain operational amplifier. It takes the differential input `(V(Vplus_opamp_node) - V(V_REF_SCHMITT_NODE))` and amplifies it by `OPAMP_GAIN_CORE` (50 Meg), saturating at `VCC_OPAMP` (5V) and `VEE_OPAMP` (0V).
    * A minimal RC filter (`R_OPAMP_FILTER`, `C_OPAMP_FILTER`) smooths the output.
* **Hysteresis Resistors:**
    * `R_SCHMITT_1 Vm Vplus_opamp_node {R_SCHMITT_1_PARAM}` (1.8k Ohms)
    * `R_SCHMITT_2 Vcomp_out Vplus_opamp_node {R_SCHMITT_2_PARAM}` (10k Ohms)
    * These two resistors form a **positive feedback loop** around the op-amp. `R_SCHMITT_1` connects the integrating membrane potential (`Vm`) to the non-inverting input (`Vplus_opamp_node`), while `R_SCHMITT_2` feeds back the output of the op-amp (`Vcomp_out`) to the same non-inverting input. This creates two distinct switching thresholds (Upper Threshold Point - UTP, and Lower Threshold Point - LTP).
* **Reference Voltage (`V_REF_SRC`):** `V_REF_SRC V_REF_SCHMITT_NODE 0 DC {V_REF_SCHMITT_PARAM}` (0.84746V)
    * A DC voltage source provides the reference voltage to the inverting input of the op-amp.
* **Thresholds (designed for):** UTP = 1.0V, LTP = 0.1V.

### 4. The Adaptive Reset Mechanism

After the neuron spikes, its membrane potential needs to be reset to prepare for the next integration cycle.

* **MOSFET Reset Switch (`Mreset`):** `Mreset Vm Vcomp_out reset_target reset_target NMOS_RESET ...`
    * An NMOS transistor `Mreset` is configured as a switch. Its drain is connected to `Vm`, and its source is connected to `reset_target` (0V, `V_RESET_VAL`).
    * Its gate is controlled by `Vcomp_out` (the output of the Schmitt trigger).
    * When `Vcomp_out` goes HIGH (indicating a spike), `Mreset` turns ON, effectively shorting `Vm` to `reset_target` (0V), rapidly discharging the memcapacitor and resetting the neuron's membrane potential.
* **Internal Upward Spike Rate Adaptation:** While the direct `Mreset` is a simple voltage clamp reset, the "upward spike rate adaptation" (facilitation) is hypothesized to emerge from the complex, non-linear dynamics of the **memcapacitor** itself, or its interaction with the feedback loop, causing the neuron to become more excitable or fire faster under sustained activation, unlike typical downward adaptation. This is an exciting emergent property to investigate.

## Simulation & Usage

This circuit is designed to be simulated using SPICE simulators (e.g., Ngspice).

### Requirements

* A SPICE simulator compatible with behavioral models (e.g., Ngspice, LTSpice).

### Running the Simulation

1.  Save the provided netlist content into a file named `neuron_circuit.cir` (or any `.cir` or `.net` extension).
2.  Open your SPICE simulator.
3.  Load and run the netlist (e.g., in Ngspice command line: `source neuron_circuit.cir`).
4.  The `.control` block within the netlist will automatically execute the simulation and save relevant output data to `output_data.txt`.

