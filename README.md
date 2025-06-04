# Hardware Spiking Fractional Leaky Integrate-and-Fire (fLIF) Neuron

## Overview & Vision

This project presents a novel, benchtop-compatible analog circuit implementation of a Fractional Leaky Integrate-and-Fire (fLIF) neuron. Unlike most state-of-the-art neuromorphic designs that require custom silicon fabrication (ASICs), this circuit is engineered to be readily buildable and testable using discrete, commercially available (or easily obtainable) components.

The purpose of this project is to address a critical gap in the neuromorphic landscape: the development of **custom, single-purpose embedded fractional-order neural "brains"** for real-world control and robotics applications. While the broader neuromorphic field is pushing towards large-scale, general-purpose computing platforms, we focus on highly efficient, compact, and specialized neural circuits capable of robust performance with remarkably few neurons.

This design specifically serves as a crucial hardware platform for:
1.  **Rapid Prototyping:** Accelerating the development and testing of fLIF neuron-based control algorithms in physical devices.
2.  **Novel Memcapacitor Research:** Providing a direct interface to benchmark and validate the neuromorphic function of physically larger, experimental memcapacitive devices (e.g., ~1 inch in size) that cannot yet be integrated into custom CMOS chips.

## Background: Fractional-Order Neurons

The field of neuromorphic engineering seeks to build artificial neural systems that mimic the structure and function of biological brains, often leveraging physical phenomena for efficient computation. A core component of such systems is the **neuron model**, which dictates how an individual artificial neuron processes input and generates output spikes.

### The Leaky Integrate-and-Fire (LIF) Model

A widely used and foundational model in computational neuroscience and neuromorphic hardware is the **Leaky Integrate-and-Fire (LIF)** neuron. In its simplest form, the membrane potential ($V_m$) of an LIF neuron evolves according to a first-order ordinary differential equation:

$$
\tau \frac{dV_m(t)}{dt} = -V_m(t) + I(t)
$$

where:
* $V_m(t)$ is the membrane potential at time $t$.
* $\tau$ is the membrane time constant.
* $I(t)$ is the input current.
* When $V_m(t)$ reaches a threshold $V_{th}$, the neuron fires a spike and is reset to $V_{reset}$.

### Limitations of Standard Integer-Order Models

While computationally efficient, standard integer-order models like the classic LIF often fall short in capturing the full spectrum of complex dynamics observed in biological neurons. These include:

* **Diverse Adaptation Patterns:** Biological neurons exhibit varied spike-frequency adaptation, bursting, and accommodation behaviors. Integer-order models often require additional, specialized conductances or variables to replicate these.
* **Intrinsic Memory:** Biological membranes are not perfectly ideal capacitors and resistors. Their ion channels and membrane structures can introduce non-ideal charge storage and leakage properties that impart a form of "intrinsic memory" to their dynamics, where the current state depends on the entire history of activity, not just the immediate past.
* **Fractional Dynamics in Biology:** Experimental evidence suggests that the impedance of biological neuron membranes can be more accurately described by fractional-order elements rather than simple integer-order capacitors. This is often attributed to anomalous diffusion of ions within the complex geometry of dendrites and axons.

### Introduction to Fractional Calculus

**Fractional calculus** is a generalization of traditional calculus that extends the concept of differentiation and integration to non-integer (fractional) orders. Instead of integer orders like $1^{st}$ derivative ($\frac{d}{dt}$) or $2^{nd}$ derivative ($\frac{d^2}{dt^2}$), fractional calculus allows for derivatives and integrals of order $\alpha$, where $\alpha$ can be any real number (e.g., $0.5, 1.3$).

The fractional derivative of order $\alpha$ (often defined by the Caputo or Riemann-Liouville definition) involves an integral over the entire history of the function, thereby inherently incorporating **long-term memory** into the system's dynamics. For a function $f(t)$, a commonly used definition is the Caputo fractional derivative:

$$
_a D_t^\alpha f(t) = \frac{1}{\Gamma(n-\alpha)} \int_a^t \frac{f^{(n)}(\tau)}{(t-\tau)^{\alpha-n+1}} d\tau
$$

where $n-1 < \alpha < n$, and $\Gamma(\cdot)$ is the Gamma function.

### Biological Motivation for Fractional-Order Neurons (fLIF)

The application of fractional calculus to neuron modeling gives rise to **Fractional Leaky Integrate-and-Fire (fLIF)** neurons. This approach is motivated by several biological observations:

* **Anomalous Diffusion:** The non-linear, fractal-like geometry of neuronal dendrites and the complex movement of ions can lead to "anomalous diffusion" phenomena, which are well-described by fractional differential equations.
* **Intrinsic Memory and Adaptation:** The history-dependent nature of fractional derivatives naturally imbues the neuron with an intrinsic memory, allowing it to capture diverse adaptation patterns (like spike-frequency adaptation or accommodation) and bursting behaviors with fewer parameters than complex integer-order models. This also accounts for the non-ideal capacitor-like behavior of biological membranes.
* **Enhanced Computational Power:** By incorporating fractional dynamics, individual neurons can exhibit richer, more complex temporal processing capabilities, potentially increasing the computational power and efficiency of neural networks.

Mathematically, an fLIF neuron's membrane potential might evolve according to a fractional differential equation:

$$
\tau^\alpha \frac{d^\alpha V_m(t)}{dt^\alpha} = -V_m(t) + I(t)
$$

where $\frac{d^\alpha}{dt^\alpha}$ denotes the fractional derivative of order $\alpha$.

### Computational Benefits of fLIF

* **Richer Dynamics:** fLIF neurons can exhibit a wide range of complex spiking behaviors, including various forms of spike-frequency adaptation, bursting, and subthreshold oscillations, using a simpler model structure than required by integer-order counterparts.
* **Reduced Parameter Count:** Often, a single fractional order parameter $\alpha$ can replace multiple additional variables or conductances required in integer-order models to achieve similar dynamic richness.
* **Improved Biological Plausibility:** They offer a more accurate phenomenological description of neuronal membrane impedance and ion channel kinetics.

### Importance of Hardware Implementation

While much research on fLIF neurons has been theoretical or simulation-based, implementing them in analog hardware is crucial for several reasons:

* **Energy Efficiency:** Analog circuits naturally embody differential equations, offering a highly energy-efficient alternative to digital simulation of complex models.
* **Real-time Processing:** Analog implementations can process signals continuously in real-time, essential for applications like robotics and control.
* **Leveraging Novel Materials:** Hardware implementations, particularly those utilizing components like memcapacitors (which inherently exhibit fractional-order properties), allow for direct experimental validation of theoretical models and exploration of emergent computational capabilities from novel materials.

This project focuses on building a benchtop-compatible fLIF neuron to facilitate hands-on experimentation with these powerful, biologically inspired dynamics.


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

## Performance & Dynamics

### Benchmarked Speed

* The circuit has been benchmarked to achieve a maximum operating frequency (firing rate) of up to **72 kHz**.
* **Comparison:** This is an excellent speed for an analog neuron circuit, significantly faster than biological neurons (tens to hundreds of Hz) and competitive with many custom analog neuromorphic implementations. It is more than sufficient for high-speed real-time control applications.

### Energy Efficiency Targets

* While detailed energy per spike measurements are ongoing, the aim is to achieve performance in the **picojoule (pJ)** range.
* Achieving **<10 pJ/spike** would be an outstanding result, putting it in a highly competitive class.
* **10 pJ to 100 pJ/spike** would be a very strong, respectable target for this type of complex, benchtop-compatible analog design.

### Bridging the Hardware Gap (Benchtop Compatibility)

* This circuit's ability to be **physically built and tested without custom silicon (ASIC)** is a critical differentiator. It removes the multi-million dollar non-recurring engineering (NRE) costs and years-long fabrication cycles associated with most neuromorphic hardware development.
* This makes it ideal for **rapid prototyping**, allowing researchers to quickly validate algorithms and explore the behavior of fractional-order neurons in real hardware.

### Enabling Novel Memcapacitor Research

* In general, researchers are developing **physically larger, novel memcapacitive devices** (~1 inch in size) that cannot currently be integrated directly onto CMOS dies.
* This circuit provides the **essential benchtop interface** to experimentally test and validate the neuromorphic function of these cutting-edge, macroscopic memcapacitors in a complete neuron context, bridging the gap between material science, device physics, and neuromorphic circuit behavior.

### Addressing the Embedded ML Niche

* This project directly tackles the often-overlooked area of **embedded machine learning** with custom hardware.
* Simulations have shown that fLIF neurons can solve complex control tasks (e.g., cart-pole, Santa Fe Trail) with **remarkably few neurons (<20)**. This demonstrates the potential for highly efficient, single-purpose analog "brains" for robotics and other edge AI applications, offering energy advantages over traditional digital processors for continuous control.

## Simulation & Usage

This circuit is designed to be simulated using SPICE simulators (e.g., Ngspice).

### Requirements

* A SPICE simulator compatible with behavioral models (e.g., Ngspice, LTSpice).

### Running the Simulation

1.  Save the provided netlist content into a file named `neuron_circuit.cir` (or any `.cir` or `.net` extension).
2.  Open your SPICE simulator.
3.  Load and run the netlist (e.g., in Ngspice command line: `source neuron_circuit.cir`).
4.  The `.control` block within the netlist will automatically execute the simulation and save relevant output data to `output_data.txt`.

### Output Data

The simulation will output the following data to `output_data.txt` (and plot in the simulator's GUI):
* `V(Vm)`: The membrane potential of the neuron (voltage across the memcapacitor).
* `V(Vcomp_out)`: The output of the Schmitt trigger (representing the neuron's spike).
* `time`: The simulation time.
* `V(Xmemcap.charge)`: Internal charge state of the memcapacitor.
* `V(Xmemcap.x)`: Internal state variable 'x' of the memcapacitor.

This data can then be analyzed using external tools (e.g., Python scripts) for spike detection, frequency analysis, and energy consumption calculations.
