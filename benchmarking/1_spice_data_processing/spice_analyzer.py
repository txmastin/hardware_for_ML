import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

def parse_ngspice_raw_txt(filepath):
    """
    Parses a raw ngspice text output file (like 'output_data.txt')
    which has a specific vertical, indexed format.

    Args:
        filepath (str): Path to the ngspice raw output file.

    Returns:
        pandas.DataFrame: DataFrame containing the simulation data,
                          or None if parsing fails.
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        num_variables = 0
        raw_variable_names = []
        data_start_line_idx = -1

        # Define col_name_map early so it's always available
        col_name_map = {
            'time': 'time',
            'v(vm)': 'Vm',
            'v(vcomp_out)': 'Vcomp_out',
            'i(v_sense_iin_p)': 'Isense_Iin',
            'i(v_sense_mreset_d)': 'Isense_Mreset'
        }

        # Phase 1: Extract metadata
        for i, line in enumerate(lines):
            if "No. Variables:" in line:
                num_variables = int(line.split(':')[1].strip())
            elif "Variables:" in line:
                # Extract variable names (e.g., 'time', 'v(vm)', 'i(v_sense_iin_p)')
                for j in range(num_variables):
                    # Line format: "    X    name     unit"
                    parts = lines[i + 1 + j].strip().split()
                    if len(parts) >= 2:
                        raw_variable_names.append(parts[1])
                    else:
                        print(f"Error: Could not parse variable name from line: '{lines[i + 1 + j].strip()}'")
                        return None
            elif "Values:" in line:
                data_start_line_idx = i + 1 # Data starts immediately after "Values:"
                break

        if num_variables == 0 or not raw_variable_names or data_start_line_idx == -1:
            print("Error: Could not extract all necessary metadata (num_variables, variable_names, data_start_line_idx).")
            return None

        # Verify raw_variable_names length
        if len(raw_variable_names) != num_variables:
            print(f"Error: Mismatch between 'No. Variables' ({num_variables}) and extracted variable names ({len(raw_variable_names)}).")
            return None

        # Phase 2: Parse actual data block
        all_data_points = []
        line_cursor = data_start_line_idx

        print(f"\nDEBUG_PARSING: Starting data parsing from line_cursor = {data_start_line_idx}")
        print(f"DEBUG_PARSING: Total lines in file: {len(lines)}")
        print(f"DEBUG_PARSING: Expected num_variables per point: {num_variables}")

        while line_cursor < len(lines):
            line_content = lines[line_cursor].strip()
            # print(f"DEBUG_PARSING: Current line_cursor: {line_cursor}, Line content: '{line_content}'") # Too verbose

            if not line_content: # Skip empty lines
                # print("DEBUG_PARSING: Skipping empty line.") # Too verbose
                line_cursor += 1
                continue
            
            # The first line of a block contains the point index AND the first variable's value
            # e.g., '0       1.000000000000000e-09'
            parts = line_content.split()
            
            if not parts: # Should not happen after .strip() and not line_content check, but for robustness
                line_cursor += 1
                continue

            try:
                # The first part is the index, the second is the first variable's value
                point_idx = int(parts[0]) # We don't use this directly for the DF, but validate it
                first_var_val = float(parts[1])
                
                current_point_data_values = [first_var_val]
                line_cursor += 1 # Move to the line of the second variable
                
                # Now read the remaining num_variables - 1 data values
                values_read_count = 1 # Already read the first one
                
                # print(f"DEBUG_PARSING: --- Reading remaining {num_variables - 1} data values for point {point_idx} ---") # Too verbose

                while values_read_count < num_variables and line_cursor < len(lines):
                    data_line = lines[line_cursor].strip()
                    # print(f"DEBUG_PARSING:   Data line {values_read_count+1}/{num_variables} at cursor {line_cursor}: '{data_line}'") # Too verbose

                    if not data_line: # Skip empty lines
                        # print("DEBUG_PARSING:   Skipping empty data line.") # Too verbose
                        line_cursor += 1
                        continue
                    
                    try:
                        current_point_data_values.append(float(data_line))
                        values_read_count += 1
                        line_cursor += 1
                    except ValueError:
                        print(f"DEBUG_PARSING:   Warning: Expected numeric data but found non-numeric '{data_line}' at line {line_cursor+1}. Stopping inner loop.")
                        break # Break inner loop
                
                if values_read_count == num_variables: # Only add if we got all values for the point
                    all_data_points.append(current_point_data_values)
                    # print(f"DEBUG_PARSING: Collected full point for index {point_idx}. Total points collected so far: {len(all_data_points)}") # Too verbose
                else:
                    print(f"DEBUG_PARSING: Incomplete data point collected for point index {point_idx}. Expected {num_variables}, got {values_read_count}. Current line_cursor: {line_cursor}. Last line processed: '{data_line if 'data_line' in locals() else line_content}'")
                
                # If the inner loop broke due to ValueError, the outer loop should also terminate
                if values_read_count < num_variables:
                    print("DEBUG_PARSING: Inner loop broke prematurely. Terminating outer loop.")
                    break
            
            except (ValueError, IndexError) as e:
                # This catches if parts[0] or parts[1] fail to convert or if parts doesn't have enough elements
                print(f"DEBUG_PARSING: Error parsing block start line '{line_content}' at line {line_cursor+1}: {e}. Breaking parsing loop.")
                break # Exit loop if we can't parse a block header

        print(f"DEBUG_PARSING: Finished data parsing. Final all_data_points count: {len(all_data_points)}")

        if not all_data_points:
            print(f"Warning: No valid data points extracted from {filepath}.")
            return pd.DataFrame(columns=[col_name_map[name] for name in raw_variable_names if name in col_name_map])

        # Phase 3: Create and Clean DataFrame (rest of function is unchanged)
        # Ensure that each collected data point has the correct number of values
        cleaned_data_points = [p for p in all_data_points if len(p) == num_variables]

        if not cleaned_data_points:
            print(f"Error: No complete data points found after cleaning for correct number of variables.")
            return None

        # Convert to DataFrame using the raw variable names extracted from header
        df = pd.DataFrame(cleaned_data_points, columns=raw_variable_names)
        
        # Apply renaming. Ensure only columns that exist and are in our map are renamed.
        df.rename(columns=col_name_map, inplace=True)

        # Ensure all required columns are present after renaming and are numeric
        required_cols = ['time', 'Vm', 'Vcomp_out', 'Isense_Iin', 'Isense_Mreset']
        if not all(col in df.columns for col in required_cols):
            print(f"Error: Not all required columns ({required_cols}) found in DataFrame after parsing and renaming.")
            print(f"Columns present: {df.columns.tolist()}")
            return None

        # Final cleanup: ensure numeric types and drop any remaining NaNs
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=required_cols, inplace=True)

        if df.empty:
            print(f"Warning: DataFrame is empty after final numeric conversion and dropna.")
            return None

        return df

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"Error during parsing: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for easier debugging
        return None

# The analyze_spice_output and if __name__ == "__main__": blocks remain unchanged
# as they call the parse_ngspice_raw_txt function.
# The analyze_spice_output and if __name__ == "__main__": blocks remain unchanged
# as they call the parse_ngspice_raw_txt function.

def analyze_spice_output(filepath="output_data.txt", VCC_OPAMP=5.0, VEE_OPAMP=0.0):
    """
    Analyzes the ngspice output data to extract neuron metrics.
    Now uses the custom parse_ngspice_raw_txt function.

    Args:
        filepath (str): Path to the ngspice output_data.txt file.
        VCC_OPAMP (float): Value of the positive op-amp supply voltage (from .param).
        VEE_OPAMP (float): Value of the negative op-amp supply voltage (from .param).

    Returns:
        dict: A dictionary containing extracted metrics (firing rate, energy per spike, etc.).
    """
    data = parse_ngspice_raw_txt(filepath)

    if data is None or data.empty:
        print(f"Error: Failed to load or parse data from {filepath}.")
        return {
            'num_spikes': 0,
            'firing_rate_hz': 0.0,
            'simulation_duration_s': 0.0,
            'total_dynamic_energy_J': 0.0,
            'energy_per_spike_J': np.nan,
            'avg_input_current_A': 0.0,
            'avg_reset_current_A': 0.0
        }

    time = data['time'].values
    vm = data['Vm'].values
    vcomp_out = data['Vcomp_out'].values
    isense_iin = data['Isense_Iin'].values
    isense_mreset = data['Isense_Mreset'].values

    # --- Spike Detection ---
    # Define Schmitt trigger thresholds based on your circuit's VCC_OPAMP and VEE_OPAMP
    schmitt_high_threshold = VCC_OPAMP * 0.8  # e.g., 80% of VCC_OPAMP
    schmitt_low_threshold = VEE_OPAMP + (VCC_OPAMP - VEE_OPAMP) * 0.2 # e.g., 20% from VEE (if VEE is 0, then 20% of VCC)

    spike_times = []
    # Look for rising edge of Vcomp_out to detect a spike
    for i in range(1, len(vcomp_out)):
        if vcomp_out[i-1] < schmitt_high_threshold and vcomp_out[i] >= schmitt_high_threshold:
            spike_times.append(time[i])

    num_spikes = len(spike_times)

    # --- Firing Rate Calculation ---
    simulation_duration = time[-1] - time[0]
    if simulation_duration <= 0:
        firing_rate_hz = 0.0
    else:
        firing_rate_hz = num_spikes / simulation_duration


    # --- Energy Calculation ---
    energy_from_input_J = np.trapz(vm * isense_iin, time)
    energy_from_reset_J = np.trapz(np.abs(vm * isense_mreset), time)
    total_dynamic_energy_J = energy_from_input_J + energy_from_reset_J
    energy_per_spike_J = total_dynamic_energy_J / num_spikes if num_spikes > 0 else np.nan


    metrics = {
        'num_spikes': num_spikes,
        'firing_rate_hz': firing_rate_hz,
        'simulation_duration_s': simulation_duration,
        'total_dynamic_energy_J': total_dynamic_energy_J,
        'energy_per_spike_J': energy_per_spike_J,
        'avg_input_current_A': np.mean(np.abs(isense_iin)),
        'avg_reset_current_A': np.mean(np.abs(isense_mreset))
    }

    return metrics

if __name__ == "__main__":
    # Example Usage:
    # Ensure you have an 'example_output_data.txt' in the same directory for testing.
    # It must be generated by:
    # 1. Going to '0_project_setup' directory.
    # 2. Temporarily replace placeholders in 'neuron_template.cir' with fixed values (e.g., I_CONST_IN=200u, T_STOP=100m, T_STEP=0.1u).
    # 3. Run: ngspice -b neuron_template.cir > ngspice_full_log.txt 2>&1
    # 4. Copy the generated 'output_data.txt' from '0_project_setup' to this '1_spice_data_processing' directory and rename it to 'example_output_data.txt'.
    # 5. Revert 'neuron_template.cir' back to placeholders in '0_project_setup'.

    # Test parameters (ensure they match your neuron_template.cir's .param values if not placeholders)
    VCC_OPAMP_VAL = 5.0
    VEE_OPAMP_VAL = 0.0

    output_file_path = "example_output_data.txt"

    analysis_results = analyze_spice_output(output_file_path, VCC_OPAMP_VAL, VEE_OPAMP_VAL)

    if analysis_results:
        print("\n--- Analysis Results ---")
        for key, value in analysis_results.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4e}")
            else:
                print(f"{key}: {value}")

        # Plotting the results for visualization
        data_to_plot = parse_ngspice_raw_txt(output_file_path)

        if data_to_plot is not None and not data_to_plot.empty:
            plt.figure(figsize=(12, 8))

            plt.subplot(3, 1, 1)
            plt.plot(data_to_plot['time'], data_to_plot['Vm'], label='Membrane Potential (Vm)')
            plt.ylabel('Voltage (V)')
            plt.title('Neuron Behavior')
            plt.grid(True)
            plt.legend()

            plt.subplot(3, 1, 2)
            plt.plot(data_to_plot['time'], data_to_plot['Vcomp_out'], label='Schmitt Trigger Output')
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.grid(True)
            plt.legend()

            plt.subplot(3, 1, 3)
            plt.plot(data_to_plot['time'], data_to_plot['Isense_Iin'] * 1e6, label='Input Current (Iin)')
            plt.plot(data_to_plot['time'], data_to_plot['Isense_Mreset'] * 1e6, label='Reset Current (Mreset)')
            plt.xlabel('Time (s)')
            plt.ylabel(r'Current ($\mu$A)')
            plt.title('Currents')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
            print("Warning: No valid data to plot after cleaning up.")
    else:
        print("No analysis results. Check for errors above.")
