import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add the directory containing spice_analyzer.py to the Python path
# This allows us to import functions from it directly
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '1_spice_data_processing'))
from spice_analyzer import analyze_spice_output # Import the analysis function

# Define paths (relative to this script's location)
BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
TEMPLATE_NETLIST_PATH = os.path.join(BASE_DIR, '0_project_setup', 'neuron_template.cir')
TEMP_NETLIST_PATH = os.path.join(os.path.dirname(__file__), 'temp_neuron_sim.cir')
OUTPUT_DATA_PATH = os.path.join(os.path.dirname(__file__), 'output_data.txt')
NGSPICE_LOG_PATH = os.path.join(os.path.dirname(__file__), 'ngspice_log.txt')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_single_spice_simulation(input_current_amp, sim_time, sim_timestep):
    """
    Modifies the template netlist, runs ngspice, and returns parsed analysis results.
    """
    print(f"Running simulation for I_in = {input_current_amp:.2e} A...")

    # 1. Read the template netlist
    try:
        with open(TEMPLATE_NETLIST_PATH, 'r') as f:
            netlist_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template netlist not found at {TEMPLATE_NETLIST_PATH}. Please check path.")
        return None

    # 2. Replace placeholders with current simulation parameters
    netlist_content = netlist_content.replace('{I_CONST_IN_PLACEHOLDER}', str(input_current_amp))
    netlist_content = netlist_content.replace('{T_STOP_PLACEHOLDER}', str(sim_time))
    netlist_content = netlist_content.replace('{T_STEP_PLACEHOLDER}', str(sim_timestep))

    # 3. Write the modified netlist to a temporary file in the current directory
    with open(TEMP_NETLIST_PATH, 'w') as f:
        f.write(netlist_content)

    # 4. Run ngspice in batch mode, redirecting output to log file
    # The 'write output_data.txt' command in .control block will create output_data.txt
    ngspice_command = f"ngspice -b {TEMP_NETLIST_PATH} > {NGSPICE_LOG_PATH} 2>&1"
    os.system(ngspice_command)

    # 5. Analyze the generated output_data.txt using our analyzer function
    # Ensure VCC_OPAMP and VEE_OPAMP match your circuit's parameters
    analysis_results = analyze_spice_output(OUTPUT_DATA_PATH, VCC_OPAMP=5.0, VEE_OPAMP=0.0)

    # Clean up temporary files (optional, but good practice)
    os.remove(TEMP_NETLIST_PATH)
    if os.path.exists(OUTPUT_DATA_PATH):
        os.remove(OUTPUT_DATA_PATH)
    if os.path.exists(NGSPICE_LOG_PATH):
        os.remove(NGSPICE_LOG_PATH)

    return analysis_results

def main():
    print("--- Starting Throughput and Max Operating Frequency Benchmark ---")

    # Define the range of input currents to sweep
    # Start from a very low current (sub-threshold) up to a high current (saturating firing rate)
    # Adjust these values based on your neuron's expected threshold and max firing rate
    input_current_amps = np.logspace(np.log10(1e-4), np.log10(1e-1), 20) # Example: 1 nA to 10 µA, 20 points
    # If your neuron fires with negative current, you might need to sweep negative values.
    # Given your Iin was -200uA, you might need to adjust the current definition or sweep negative values.
    # For simplicity, let's assume Iin pushes current into Vm to make it spike (positive current).
    # If your neuron fires with -200uA, it means it's current *drawn* from Vm.
    # For a standard I-F curve, current is usually supplied to the neuron.
    # Let's adjust this. If your neuron fires with current OUT of the supply (i.e. -Iin in plot),
    # then positive Iin should mean current *into* Vm.
    # For an I-F curve, it's typically how neuron responds to increasing *excitatory* input.
    # So let's sweep positive currents for now, assuming standard LIF behavior.
    # If your neuron requires negative input current to spike, you'd make this range negative.

    # Simulation time and timestep
    # T_STOP needs to be long enough to capture multiple spikes for stable frequency measurement
    # T_STEP needs to be small enough for accurate simulation, especially at high firing rates
    SIM_TIME = 0.1 # seconds (100 ms)
    SIM_TIMESTEP = 0.1e-6 # seconds (100 ns)

    benchmark_results = []

    for i_amp in input_current_amps:
        # For each current, run a simulation
        results = run_single_spice_simulation(i_amp, SIM_TIME, SIM_TIMESTEP)
        if results:
            results['input_current_A'] = i_amp
            benchmark_results.append(results)
        else:
            print(f"Skipping {i_amp:.2e} A due to simulation/analysis error.")

    if not benchmark_results:
        print("No benchmark results collected. Please check simulation and analysis errors.")
        return

    # Convert results to DataFrame for easier plotting and saving
    df_results = pd.DataFrame(benchmark_results)

    # --- Plotting the I-F Curve ---
    plt.figure(figsize=(10, 6))
    plt.plot(df_results['input_current_A'] * 1e6, df_results['firing_rate_hz'], 'o-', label='Firing Rate')
    plt.xlabel('Input Current ($\mu$A)')
    plt.ylabel('Firing Rate (Hz)')
    plt.title('Neuron I-F Curve')
    plt.grid(True)
    plt.xscale('log') # Use log scale for input current if sweeping a wide range
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'if_curve.png'))
    print(f"I-F curve saved to {os.path.join(RESULTS_DIR, 'if_curve.png')}")
    # plt.show() # Uncomment to display plot interactively

    # --- Plotting Energy per Spike ---
    # Filter out rows where num_spikes is 0, as energy_per_spike will be NaN
    df_fired = df_results[df_results['num_spikes'] > 0].copy()

    if not df_fired.empty:
        plt.figure(figsize=(10, 6))
        plt.plot(df_fired['firing_rate_hz'], df_fired['energy_per_spike_J'] * 1e12, 'o-', label='Energy per Spike') # pJ
        plt.xlabel('Firing Rate (Hz)')
        plt.ylabel('Energy per Spike (pJ)')
        plt.title('Energy Efficiency vs. Firing Rate')
        plt.grid(True)
        plt.yscale('log') # Energy can vary by orders of magnitude
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(RESULTS_DIR, 'energy_per_spike.png'))
        print(f"Energy per spike curve saved to {os.path.join(RESULTS_DIR, 'energy_per_spike.png')}")
        # plt.show() # Uncomment to display plot interactively
    else:
        print("No spikes detected across any input current for energy per spike plot.")

    # --- Save Raw Benchmark Data ---
    df_results.to_csv(os.path.join(RESULTS_DIR, 'if_benchmark_data.csv'), index=False)
    print(f"Benchmark data saved to {os.path.join(RESULTS_DIR, 'if_benchmark_data.csv')}")

    # --- Report Max Operating Frequency ---
    max_freq = df_results['firing_rate_hz'].max()
    print(f"\n--- Benchmark Summary ---")
    print(f"Maximum Operating Frequency (Throughput): {max_freq:.2f} Hz")
    print(f"Number of simulation runs: {len(df_results)}")


if __name__ == '__main__':
    main()
