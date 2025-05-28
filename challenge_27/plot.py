import numpy as np
import matplotlib.pyplot as plt

def analyze_spike_adaptation(filepath="output_data.txt", threshold=2.5, min_isi=1e-6):
    """
    Analyzes spike rate adaptation from ngspice output data.

    Args:
        filepath (str): Path to the ngspice output data file (e.g., 'output_data.txt').
        threshold (float): Voltage threshold for detecting spikes from Vcomp_out.
        min_isi (float): Minimum inter-spike interval to filter out spurious detections
                         due to simulation noise or very fast switching.
    """
    try:
        time = []
        vm = []
        vcomp_out = []

        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Find the "Values:" line
        start_data_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "Values:":
                start_data_idx = i + 1
                break

        if start_data_idx == -1:
            raise ValueError("Could not find 'Values:' header in the data file.")

        # Parse the data
        current_point_data = []
        for line in lines[start_data_idx:]:
            stripped_line = line.strip()
            if not stripped_line: # Skip empty lines
                continue

            parts = stripped_line.split()

            # Check if it's a new data point (starts with an integer index)
            # This is robust because the index is always an integer followed by a value
            if len(parts) == 2 and parts[0].isdigit():
                # This is the start of a new data point: index and time
                if current_point_data: # If we have data from the previous point, store it
                    time.append(current_point_data[0])
                    vm.append(current_point_data[1])
                    vcomp_out.append(current_point_data[2])
                current_point_data = [float(parts[1])] # Store time as the first element
            elif len(parts) == 1:
                # These are the subsequent data values (Vm, Vcomp_out)
                current_point_data.append(float(parts[0]))
            else:
                # Handle any unexpected line formats or errors
                print(f"Warning: Skipping unparseable line: {line.strip()}")
                continue # Skip this line and try to continue

        # Append the last collected data point after the loop finishes
        if current_point_data:
            time.append(current_point_data[0])
            vm.append(current_point_data[1])
            vcomp_out.append(current_point_data[2])

        time = np.array(time)
        vm = np.array(vm)
        vcomp_out = np.array(vcomp_out)

    except Exception as e:
        print(f"Error loading and parsing data from {filepath}: {e}")
        print("Please ensure the ngspice 'write' command and file path are correct.")
        return

    # --- Spike Detection ---
    spike_times = []
    # Iterate through Vcomp_out to detect rising edges
    for i in range(1, len(vcomp_out)):
        if vcomp_out[i] >= threshold and vcomp_out[i-1] < threshold:
            spike_times.append(time[i])

    print(f"Detected {len(spike_times)} spikes.")

    # --- Calculate ISIs ---
    if len(spike_times) < 2:
        print("Not enough spikes to calculate ISIs.")
        return

    isis = []
    isi_mid_times = [] # Time point at the midpoint of the ISI for plotting
    for i in range(1, len(spike_times)):
        current_isi = spike_times[i] - spike_times[i-1]
        if current_isi > min_isi: # Filter out very small, possibly spurious ISIs
            isis.append(current_isi)
            isi_mid_times.append((spike_times[i] + spike_times[i-1]) / 2)


    # --- Calculate Instantaneous Firing Rate (1/ISI) ---
    if not isis:
        print("No valid ISIs to calculate firing rate.")
        return

    firing_rates = [1.0 / isi for isi in isis]


    # --- Plotting ---
    plt.figure(figsize=(12, 8))

    # Plot Membrane Potential and Schmitt Trigger Output
    plt.subplot(3, 1, 1)
    plt.plot(time, vm, label='Vm')
    plt.plot(time, vcomp_out, label='Vcomp_out (Schmitt Trigger)')
    plt.axhline(threshold, color='red', linestyle='--', label='Spike Detection Threshold')
    for s_time in spike_times:
        plt.axvline(s_time, color='gray', linestyle=':', linewidth=0.8)
    plt.title('Membrane Potential and Schmitt Trigger Output')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.legend()
    plt.grid(True)

    # Plot ISIs over time
    plt.subplot(3, 1, 2)
    plt.plot(isi_mid_times, isis, 'o-', markersize=4, label='ISI')
    plt.title('Inter-Spike Interval (ISI) vs. Time')
    plt.xlabel('Time (s)')
    plt.ylabel('ISI (s)')
    plt.grid(True)

    # Plot Instantaneous Firing Rate (1/ISI) over time
    plt.subplot(3, 1, 3)
    plt.plot(isi_mid_times, firing_rates, 'o-', markersize=4, color='green', label='Firing Rate (1/ISI)')
    plt.title('Instantaneous Firing Rate vs. Time (Spike Rate Adaptation)')
    plt.xlabel('Time (s)')
    plt.ylabel('Firing Rate (Hz)')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# --- Run the analysis ---
if __name__ == "__main__":
    analyze_spike_adaptation(filepath="output_data.txt", threshold=2.5, min_isi=1e-6)
