import numpy as np
import random
from trail import load_santa_fe_trail # Assuming this is available
import time # Import time module for profiling

# --- Constants and Hyperparameters ---
# Environment
GRID_SIZE = 32
MAX_STEPS_PER_EPISODE = 250
TOTAL_FOOD_PELLETS_ON_MAP = 89
START_POS = (0, 0)  # Assuming top-left, adjust based on map
START_ORIENTATION = 'EAST' # Example, adjust based on map (0:E, 1:S, 2:W, 3:N)

# SNN Parameters
FLIF_MEMBRANE_TIME_CONSTANT = 20.0  # ms
FLIF_THRESHOLD_VOLTAGE = 0.3    # mV (or normalized units)
FLIF_RESET_VOLTAGE = 0.0    # mV
FLIF_NEURONS_BIAS = 0.05    # Small bias
FLIF_FRACTIONAL_ORDER_ALPHA = 0.75
FLIF_MEMORY_LENGTH = 12500 # This directly impacts np.dot and np.roll time

LIF_MEMBRANE_TIME_CONSTANT = 20.0  # ms
LIF_THRESHOLD_VOLTAGE = 0.75      # mV
LIF_RESET_VOLTAGE = 0.0          # mV
LIF_NEURONS_BIAS = 0.05

DT_NEURON_SIM = 0.1             # ms
T_ANT_DECISION_WINDOW = 5.0      # ms
NUM_NEURON_STEPS_PER_ANT_STEP = int(T_ANT_DECISION_WINDOW / DT_NEURON_SIM)

I_ACTIVE_INPUT_CURRENT = 1.5     # Current injected when context is active

# RL Parameters
LEARNING_RATE_ETA = 0.0001
DISCOUNT_FACTOR_GAMMA = 0.99
EXPLORATION_TEMPERATURE_TAU_RL = 1.0 # For softmax

# Surrogate Gradient
SG_RECT_WIDTH = 0.5            # mV

# Action Mapping
ACTION_MAP = {0: 'TurnLeft', 1: 'TurnRight', 2: 'MoveForward'}
ACTION_IDX_MAP = {'TurnLeft':0, 'TurnRight':1, 'MoveForward':2} # For convenience

NUM_EPISODES = 1000 # Example number of training episodes

# --- Helper Functions ---
def calculate_gl_coefficients(alpha, length):
    coeffs = np.zeros(length, dtype=np.float64)
    if length == 0:
        return coeffs
    coeffs[0] = -alpha # Matches user's Cython code
    for j in range(1, length):
        coeffs[j] = (1.0 - (alpha + 1.0) / (j + 1.0)) * coeffs[j-1] # j+1 to match Cython's j indexing
    return coeffs

def softmax_stable(logits_array):
    if not logits_array.size: return np.array([]) # Handle empty array
    stable_logits = logits_array - np.max(logits_array)
    exp_logits = np.exp(stable_logits)
    sum_exp_logits = np.sum(exp_logits)
    if sum_exp_logits == 0: # Avoid division by zero if all logits are extremely small
        return np.ones_like(exp_logits) / exp_logits.size
    return exp_logits / sum_exp_logits

def calculate_discounted_returns(rewards_list, gamma):
    G = 0.0
    discounted_returns = np.zeros_like(rewards_list, dtype=float)
    for t in reversed(range(len(rewards_list))):
        G = rewards_list[t] + gamma * G
        discounted_returns[t] = G
    return discounted_returns

def rectangular_surrogate_gradient(membrane_potential, threshold, width):
    u = membrane_potential - threshold
    if abs(u) < width / 2.0:
        return 1.0 / width
    return 0.0

def initialize_weights(num_weights):
    return (np.random.rand(num_weights)) * 0.1 + 0.1

# --- Neuron Classes ---
class FractionalLIFNeuron:
    def __init__(self, neuron_id, params):
        self.neuron_id = neuron_id
        self.alpha = params.get("alpha", FLIF_FRACTIONAL_ORDER_ALPHA)
        self.tau_m = params.get("tau_m", FLIF_MEMBRANE_TIME_CONSTANT)
        self.V_th = params.get("V_th", FLIF_THRESHOLD_VOLTAGE)
        self.V_reset = params.get("V_reset", FLIF_RESET_VOLTAGE)
        self.bias = params.get("bias", FLIF_NEURONS_BIAS)
        self.memory_length = params.get("memory_length", FLIF_MEMORY_LENGTH)
        
        self.V = self.V_reset
        self.voltage_history = np.full(self.memory_length, self.V_reset, dtype=np.float64)
        self.gl_coefficients = calculate_gl_coefficients(self.alpha, self.memory_length)
        self.spike_state = 0

    def reset_state(self):
        self.V = self.V_reset
        self.voltage_history.fill(self.V_reset)
        self.spike_state = 0

    def update(self, input_current, dt):
        self.spike_state = 0
        
        # --- Start timing for fractional order calculation (np.dot) ---
        frac_calc_start_time = time.perf_counter()

        history_component = 0.0
        if self.memory_length > 0:
            history_component = np.dot(self.gl_coefficients, self.voltage_history)

        frac_calc_end_time = time.perf_counter()
        # --- End timing for fractional order calculation ---

        kernel = dt**self.alpha
        
        effective_dV_dt_part = (-self.V / self.tau_m) + self.bias + input_current
        
        self.V = effective_dV_dt_part * kernel - history_component
        
        if self.V >= self.V_th:
            self.spike_state = 1
            self.V = self.V_reset
            
        # --- Start timing for history update (np.roll) ---
        history_update_start_time = time.perf_counter()
        if self.memory_length > 0:
            self.voltage_history = np.roll(self.voltage_history, 1)
            self.voltage_history[0] = self.V # Store post-reset or current subthreshold V
        history_update_end_time = time.perf_counter()
        # --- End timing for history update ---

        # Return the spike state and the time taken for fractional specific operations
        return self.spike_state, (frac_calc_end_time - frac_calc_start_time), (history_update_end_time - history_update_start_time)

    def get_spike_state(self):
        return self.spike_state

    def get_voltage(self):
        return self.V

class StandardLIFNeuron:
    def __init__(self, neuron_id, params):
        self.neuron_id = neuron_id
        self.tau_m = params.get("tau_m", LIF_MEMBRANE_TIME_CONSTANT)
        self.V_th = params.get("V_th", LIF_THRESHOLD_VOLTAGE)
        self.V_reset = params.get("V_reset", LIF_RESET_VOLTAGE)
        self.bias_current = params.get("bias_current", LIF_NEURONS_BIAS) # Assuming bias is a current
        
        self.V = self.V_reset
        self.spike_state = 0

    def reset_state(self):
        self.V = self.V_reset
        self.spike_state = 0

    def update(self, input_current, dt):
        self.spike_state = 0
        
        dV_dt = (-self.V / self.tau_m) + self.bias_current + input_current # if bias and input_current are currents scaled by 1/C
        self.V += dV_dt * dt

        if self.V >= self.V_th:
            self.spike_state = 1
            self.V = self.V_reset
            
        # Return 0 for timing for standard LIF neurons, as they don't have fractional ops
        return self.spike_state, 0.0, 0.0

    def get_spike_state(self):
        return self.spike_state

    def get_voltage(self):
        return self.V

# --- Environment Class ---
class SantaFeEnvironment:
    def __init__(self, map_filepath, start_pos, start_orientation_str):
        self.trail_map_original = self._load_map(map_filepath)
        self.trail_map_current = np.copy(self.trail_map_original)
        self.start_pos = start_pos
        self.start_orientation_str = start_orientation_str # 'EAST', 'SOUTH', 'WEST', 'NORTH'
        self.orientations = ['EAST', 'SOUTH', 'WEST', 'NORTH']
        self.orientation_deltas = { # dx, dy
            'EAST': (1, 0), 'SOUTH': (0, 1), 'WEST': (-1, 0), 'NORTH': (0, -1)
        }
        self.ant_pos = None
        self.ant_orientation_idx = None # Index in self.orientations
        self.food_eaten_in_episode = 0
        self.grid_height, self.grid_width = self.trail_map_original.shape

    def _load_map(self, filepath):
        print(f"Placeholder: Load Koza trail map from {filepath}")
        # Ensure 'trail' module is available in your environment for load_santa_fe_trail
        # For a quick test, you might use a dummy map if load_santa_fe_trail is not set up
        # simple_map = np.zeros((32,32), dtype=int)
        # simple_map[10,:] = 1; simple_map[:,10] = 1; # Example dummy trail
        # return simple_map
        return load_santa_fe_trail()

    def reset_ant_and_trail(self):
        self.trail_map_current = np.copy(self.trail_map_original)
        self.ant_pos = list(self.start_pos)
        self.ant_orientation_idx = self.orientations.index(self.start_orientation_str)
        self.food_eaten_in_episode = 0
        return tuple(self.ant_pos), self.orientations[self.ant_orientation_idx], np.sum(self.trail_map_current)

    def get_food_ahead(self):
        dx, dy = self.orientation_deltas[self.orientations[self.ant_orientation_idx]]
        front_x, front_y = self.ant_pos[0] + dx, self.ant_pos[1] + dy
        
        if 0 <= front_x < self.grid_width and 0 <= front_y < self.grid_height:
            return self.trail_map_current[front_y, front_x] == 1 # Assuming map is (y,x)
        return False # Off grid means no food

    def step(self, action_idx): # action_idx: 0:L, 1:R, 2:Fwd
        action_str = ACTION_MAP[action_idx]
        reward = -0.01 # Default step cost
        episode_done_env = False
        food_consumed_flag = False
        prev_pos = list(self.ant_pos)

        if action_str == 'TurnLeft':
            self.ant_orientation_idx = (self.ant_orientation_idx - 1 + 4) % 4
        elif action_str == 'TurnRight':
            self.ant_orientation_idx = (self.ant_orientation_idx + 1) % 4
        elif action_str == 'MoveForward':
            dx, dy = self.orientation_deltas[self.orientations[self.ant_orientation_idx]]
            next_x, next_y = self.ant_pos[0] + dx, self.ant_pos[1] + dy

            if 0 <= next_x < self.grid_width and 0 <= next_y < self.grid_height:
                self.ant_pos = [next_x, next_y]
                if self.trail_map_current[next_y, next_x] == 1:
                    reward = 1.0 # Food reward
                    self.trail_map_current[next_y, next_x] = 0 # Eat food
                    self.food_eaten_in_episode += 1
                    food_consumed_flag = True
                    if self.food_eaten_in_episode == TOTAL_FOOD_PELLETS_ON_MAP: # Use actual total from loaded map
                        episode_done_env = True
            else:
                # Bumped boundary, stays in place, reward is already -0.01 (step_cost)
                pass
            
        return tuple(self.ant_pos), self.orientations[self.ant_orientation_idx], reward, episode_done_env, food_consumed_flag

# --- MAIN SIMULATION AND TRAINING LOOP ---

# Initialize SNN
flif_neuron_params = {
    "alpha": FLIF_FRACTIONAL_ORDER_ALPHA, "tau_m": FLIF_MEMBRANE_TIME_CONSTANT,
    "V_th": FLIF_THRESHOLD_VOLTAGE, "V_reset": FLIF_RESET_VOLTAGE,
    "bias": FLIF_NEURONS_BIAS, "memory_length": FLIF_MEMORY_LENGTH
}
# Total 8 FLIF neurons for context/action
fLIF_food = FractionalLIFNeuron("food_ctx", flif_neuron_params)
fLIF_nofood = FractionalLIFNeuron("nofood_ctx", flif_neuron_params)
action_leaf_neurons_food_context = [FractionalLIFNeuron(f"food_leaf_{i}", flif_neuron_params) for i in range(3)]
action_leaf_neurons_nofood_context = [FractionalLIFNeuron(f"nofood_leaf_{i}", flif_neuron_params) for i in range(3)]

# A dummy LIF neuron for the params object, not used in actual computation for FLIF timing
# Ensure all relevant neurons are FLIF for the timing to be fully representative of FLIF ops
# if any of these were StandardLIF, their timings would be 0, skewing the overall sum
all_flif_neurons = [fLIF_food, fLIF_nofood] + action_leaf_neurons_food_context + action_leaf_neurons_nofood_context
NUM_FLIF_NEURONS_IN_NETWORK = len(all_flif_neurons) # Should be 8 (2+3+3)

lif_leaf_params = {
    "tau_m": LIF_MEMBRANE_TIME_CONSTANT, "V_th": LIF_THRESHOLD_VOLTAGE,
    "V_reset": LIF_RESET_VOLTAGE, "bias_current": LIF_NEURONS_BIAS # Assuming bias is current
}

W_food_to_action = initialize_weights(3)
W_nofood_to_action = initialize_weights(3)

# Initialize Environment
environment = SantaFeEnvironment("koza_trail.txt", START_POS, START_ORIENTATION)

print(f"Starting training for {NUM_EPISODES} episodes...")

# --- Timings Accumulators ---
total_sim_neuron_update_time_overall = 0.0 # Total time spent in ALL neuron updates across all episodes
total_frac_dot_time_overall = 0.0 # Total time spent in np.dot for fractional component across all episodes
total_frac_roll_time_overall = 0.0 # Total time spent in np.roll for history update across all episodes

# Global lists to store per-ant-step timings to see trends/averages
frac_dot_times_per_ant_step_list = []
frac_roll_times_per_ant_step_list = []
neuron_update_times_per_ant_step_list = [] # Total time for all neuron updates in a single ant step

overall_training_start_time = time.perf_counter() # Overall training loop timer

for episode_i in range(NUM_EPISODES):
    # Reset states for new episode
    environment.reset_ant_and_trail() # Returns ant_pos, ant_orient_str, but we overwrite below
    avg_food_eaten = 0 
    for neuron_instance in all_flif_neurons:
        neuron_instance.reset_state()

    episode_trajectory = []
    total_episode_reward = 0.0
    food_eaten_this_episode = 0

    ant_pos, ant_orient_str, _ = environment.ant_pos, environment.orientations[environment.ant_orientation_idx], environment.food_eaten_in_episode # Get initial state after reset

    for t_ant_step in range(MAX_STEPS_PER_EPISODE):
        ant_step_neuron_update_start_time = time.perf_counter() # Start timing for all neuron updates in this ant step

        is_food_ahead = environment.get_food_ahead()

        active_fLIF = fLIF_food if is_food_ahead else fLIF_nofood
        inactive_fLIF = fLIF_nofood if is_food_ahead else fLIF_food
        
        current_input_to_active_fLIF = I_ACTIVE_INPUT_CURRENT
        current_input_to_inactive_fLIF = 0.0
        
        active_leaf_neurons = action_leaf_neurons_food_context if is_food_ahead else action_leaf_neurons_nofood_context
        active_weights = W_food_to_action if is_food_ahead else W_nofood_to_action

        fLIF_spike_trace_this_T_ant = np.zeros(NUM_NEURON_STEPS_PER_ANT_STEP, dtype=int)
        leaf_potentials_this_T_ant = [np.zeros(NUM_NEURON_STEPS_PER_ANT_STEP) for _ in range(3)]
        current_T_ant_leaf_spike_counts = np.zeros(3, dtype=int)

        # Accumulators for this specific ant step's neuron updates
        ant_step_frac_dot_time_sum = 0.0
        ant_step_frac_roll_time_sum = 0.0

        for t_neuron_idx in range(NUM_NEURON_STEPS_PER_ANT_STEP):
            # Update active context fLIF
            active_fLIF_spike_state, active_fLIF_dot_time, active_fLIF_roll_time = active_fLIF.update(current_input_to_active_fLIF, DT_NEURON_SIM)
            fLIF_spike_trace_this_T_ant[t_neuron_idx] = active_fLIF_spike_state
            ant_step_frac_dot_time_sum += active_fLIF_dot_time
            ant_step_frac_roll_time_sum += active_fLIF_roll_time

            # Update inactive context fLIF
            inactive_fLIF_spike_state, inactive_fLIF_dot_time, inactive_fLIF_roll_time = inactive_fLIF.update(current_input_to_inactive_fLIF, DT_NEURON_SIM)
            ant_step_frac_dot_time_sum += inactive_fLIF_dot_time
            ant_step_frac_roll_time_sum += inactive_fLIF_roll_time
            
            for i_leaf in range(3):
                leaf_neuron = active_leaf_neurons[i_leaf] # These are also FLIF neurons
                weight = active_weights[i_leaf]
                synaptic_current_to_leaf = fLIF_spike_trace_this_T_ant[t_neuron_idx] * weight
                
                # Leaf neurons are FLIF, collect their timings
                leaf_spike_state, leaf_dot_time, leaf_roll_time = leaf_neuron.update(synaptic_current_to_leaf, DT_NEURON_SIM)
                if leaf_spike_state == 1:
                    current_T_ant_leaf_spike_counts[i_leaf] += 1
                leaf_potentials_this_T_ant[i_leaf][t_neuron_idx] = leaf_neuron.get_voltage()
                
                ant_step_frac_dot_time_sum += leaf_dot_time
                ant_step_frac_roll_time_sum += leaf_roll_time

        ant_step_neuron_update_end_time = time.perf_counter() # End timing for all neuron updates in this ant step
        current_ant_step_neuron_update_duration = ant_step_neuron_update_end_time - ant_step_neuron_update_start_time

        # Store for analysis of trends
        frac_dot_times_per_ant_step_list.append(ant_step_frac_dot_time_sum)
        frac_roll_times_per_ant_step_list.append(ant_step_frac_roll_time_sum)
        neuron_update_times_per_ant_step_list.append(current_ant_step_neuron_update_duration)

        # Accumulate total times for the final overall report
        total_sim_neuron_update_time_overall += current_ant_step_neuron_update_duration
        total_frac_dot_time_overall += ant_step_frac_dot_time_sum
        total_frac_roll_time_overall += ant_step_frac_roll_time_sum
        
        # --- End of neuron simulation for this ant step ---

        action_probabilities = softmax_stable(current_T_ant_leaf_spike_counts / EXPLORATION_TEMPERATURE_TAU_RL)
        
        # Handle case where all spike counts are zero -> uniform probabilities
        if np.sum(current_T_ant_leaf_spike_counts) == 0 :
             action_probabilities = np.ones(3) / 3.0

        chosen_action_idx = np.random.choice(3, p=action_probabilities)
        
        next_ant_pos, next_ant_orient_str, reward, episode_done_env, food_consumed_flag = \
            environment.step(chosen_action_idx)
        
        total_episode_reward += reward
        if food_consumed_flag:
             food_eaten_this_episode +=1

        episode_trajectory.append({
            "is_food_ahead_context": is_food_ahead,
            "fLIF_spike_trace": np.copy(fLIF_spike_trace_this_T_ant),
            "leaf_potentials_traces": [np.copy(p_trace) for p_trace in leaf_potentials_this_T_ant],
            "chosen_action_idx": chosen_action_idx,
            "action_probabilities": np.copy(action_probabilities),
            "reward": reward
        })

        ant_pos, ant_orient_str = next_ant_pos, next_ant_orient_str # Update ant's state string for orientation
        if episode_done_env or food_eaten_this_episode == TOTAL_FOOD_PELLETS_ON_MAP:
            break
            
    # --- End of Ant Step Loop ---
    # RL Update (Policy Gradient like)
    rewards_for_G_t = [t["reward"] for t in episode_trajectory]
    discounted_returns_G_t = calculate_discounted_returns(rewards_for_G_t, DISCOUNT_FACTOR_GAMMA)
    if len(discounted_returns_G_t) > 1:
        mean_G_t = np.mean(discounted_returns_G_t)
        std_G_t = np.std(discounted_returns_G_t)
        if std_G_t > 1e-8: # Add a small epsilon to prevent division by zero if all G_t are the same
            normalized_G_t_values = (discounted_returns_G_t - mean_G_t) / std_G_t
        else:
            normalized_G_t_values = discounted_returns_G_t - mean_G_t # Just center if std is tiny
    elif len(discounted_returns_G_t) == 1:
        normalized_G_t_values = discounted_returns_G_t # Or set to 0 if only one step, as G_0 - mean(G_0) = 0
                                                        
    else: # No transitions
        normalized_G_t_values = np.array([])

    delta_W_food_to_action = np.zeros(3)
    delta_W_nofood_to_action = np.zeros(3)
    for t_idx, transition in enumerate(episode_trajectory):
        G_t = discounted_returns_G_t[t_idx]
        if normalized_G_t_values.size > 0: # Ensure trajectory was not empty
            G_t_to_use = normalized_G_t_values[t_idx] 
        else: # Should not happen if episode_trajectory has items
            G_t_to_use = 0  
        active_weights_grad_delta_ref = delta_W_food_to_action if transition["is_food_ahead_context"] else delta_W_nofood_to_action
        
        active_leaf_neuron_params = lif_leaf_params # These params are for the surrogate gradient calculation, not the neuron update itself

        for k_action_idx in range(3): # For each of the 3 active weights
            # Approx dN_k / dw_k 
            # This is where the surrogate gradient for the leaf neuron and presynaptic activity are used
            dNk_dwk_approx = 0.0
            fLIF_spikes_for_grad = transition["fLIF_spike_trace"]
            leaf_k_potentials_for_grad = transition["leaf_potentials_traces"][k_action_idx]
            
            for t_prime_idx in range(len(fLIF_spikes_for_grad)):
                sg_val = rectangular_surrogate_gradient(
                    leaf_k_potentials_for_grad[t_prime_idx],
                    active_leaf_neuron_params["V_th"], # Using V_th from params dict
                    SG_RECT_WIDTH
                )
                if sg_val > 0: # If leaf neuron was "sensitive"
                    dNk_dwk_approx += fLIF_spikes_for_grad[t_prime_idx] # Add presynaptic spike
            
            indicator = 1.0 if k_action_idx == transition["chosen_action_idx"] else 0.0
            prob_ak = transition["action_probabilities"][k_action_idx]
            
            grad_log_pi_component = (indicator - prob_ak) * \
                                    (1.0 / EXPLORATION_TEMPERATURE_TAU_RL) * dNk_dwk_approx
            
            active_weights_grad_delta_ref[k_action_idx] += G_t_to_use * grad_log_pi_component
    
    max_grad_abs_val = 50.0  # **Tune this value carefully!** Start with something like 1.0 or 5.0.

    np.clip(delta_W_food_to_action, -max_grad_abs_val, max_grad_abs_val, out=delta_W_food_to_action)
    np.clip(delta_W_nofood_to_action, -max_grad_abs_val, max_grad_abs_val, out=delta_W_nofood_to_action)

    W_food_to_action += LEARNING_RATE_ETA * delta_W_food_to_action
    W_nofood_to_action += LEARNING_RATE_ETA * delta_W_nofood_to_action

    window = 10
    if (episode_i+1) % window == 0:  
        avg_food_eaten += food_eaten_this_episode
        avg_food_eaten /= window
        print(f"Episode {episode_i+1}: Steps={t_ant_step+1}, Average Food Eaten={avg_food_eaten}, Total Reward={total_episode_reward:.2f}, "
              f"W_food=[{W_food_to_action[0]:.3f}, {W_food_to_action[1]:.3f}, {W_food_to_action[2]:.3f}], "
              f"W_nofood=[{W_nofood_to_action[0]:.3f}, {W_nofood_to_action[1]:.3f}, {W_nofood_to_action[2]:.3f}]")
        avg_food_eaten = 0
    else:
        avg_food_eaten += food_eaten_this_episode

overall_training_end_time = time.perf_counter() # Overall training loop timer
print("Training finished.")

# --- Final Python Emulation Timing Report ---
print("\n--- Python Emulation Timing Report ---")
total_overall_training_duration = overall_training_end_time - overall_training_start_time

print(f"Total overall training duration: {total_overall_training_duration:.4f} seconds")

num_ant_steps_processed = len(neuron_update_times_per_ant_step_list)

if num_ant_steps_processed > 0:
    print(f"Total Ant Steps Processed by Neuron Simulation: {num_ant_steps_processed}")
    
    avg_neuron_update_time_per_ant_step = np.mean(neuron_update_times_per_ant_step_list)
    avg_frac_dot_time_per_ant_step = np.mean(frac_dot_times_per_ant_step_list)
    avg_frac_roll_time_per_ant_step = np.mean(frac_roll_times_per_ant_step_list)

    print(f"Average Time for ALL Neuron Updates per Ant Step: {avg_neuron_update_time_per_ant_step * 1e6:.2f} µs")
    print(f"  (This includes {NUM_FLIF_NEURONS_IN_NETWORK} FLIF neurons, each updated {NUM_NEURON_STEPS_PER_ANT_STEP} times)")
    print(f"Average Time for Fractional Dot Product (per Ant Step, all neurons): {avg_frac_dot_time_per_ant_step * 1e6:.2f} µs")
    print(f"Average Time for Fractional Roll (per Ant Step, all neurons): {avg_frac_roll_time_per_ant_step * 1e6:.2f} µs")

    # Proportions relative to the *neuron update part* of the simulation
    if avg_neuron_update_time_per_ant_step > 0:
        proportion_frac_dot_of_neuron_updates = avg_frac_dot_time_per_ant_step / avg_neuron_update_time_per_ant_step
        proportion_frac_roll_of_neuron_updates = avg_frac_roll_time_per_ant_step / avg_neuron_update_time_per_ant_step
        total_frac_ops_proportion_of_neuron_updates = proportion_frac_dot_of_neuron_updates + proportion_frac_roll_of_neuron_updates
        
        print(f"\nProportion of Neuron Update Time spent on Fractional Dot Product: {proportion_frac_dot_of_neuron_updates:.4f} ({proportion_frac_dot_of_neuron_updates*100:.2f}%)")
        print(f"Proportion of Neuron Update Time spent on Fractional Roll: {proportion_frac_roll_of_neuron_updates:.4f} ({proportion_frac_roll_of_neuron_updates*100:.2f}%)")
        print(f"Total Proportion of Neuron Update Time on Core Fractional Ops (Dot + Roll): {total_frac_ops_proportion_of_neuron_updates:.4f} ({total_frac_ops_proportion_of_neuron_updates*100:.2f}%)")
    
    # Proportions relative to overall training time (if training dominates neuron updates)
    if total_overall_training_duration > 0:
        proportion_neuron_updates_of_total_training = total_sim_neuron_update_time_overall / total_overall_training_duration
        print(f"\nProportion of Total Overall Training Duration spent in ALL Neuron Updates: {proportion_neuron_updates_of_total_training:.4f} ({proportion_neuron_updates_of_total_training*100:.2f}%)")
        print(f"Proportion of Total Overall Training Duration spent on Fractional Dot Product: {(total_frac_dot_time_overall / total_overall_training_duration):.4f} ({(total_frac_dot_time_overall / total_overall_training_duration)*100:.2f}%)")
        print(f"Proportion of Total Overall Training Duration spent on Fractional Roll: {(total_frac_roll_time_overall / total_overall_training_duration):.4f} ({(total_frac_roll_time_overall / total_overall_training_duration)*100:.2f}%)")

else:
    print("No ant steps processed. Check MAX_STEPS_PER_EPISODE or NUM_EPISODES.")

# --- Analysis of History Length Effect ---
print("\n--- Analysis of Fractional Derivative Cost vs. History Length ---")
print(f"Note: In this current code, 'memory_length' (set to {FLIF_MEMORY_LENGTH}) is fixed at initialization.")
print("The time taken for the `np.dot` operation (fractional derivative core) per neuron update call should be relatively constant, as it operates on a fixed-size array.")
print("The 'growing compute time due to the full memory trace needing to be computed at each dt' typically refers to implementations where the fractional derivative explicitly sums over an *ever-growing* history from the start of the simulation.")
print("To observe such a *dynamically increasing* cost per step in Python, you would need to modify the `FractionalLIFNeuron.update` method such that `self.voltage_history` (and `self.gl_coefficients` if recomputed) effectively grows in size with `t_neuron_idx` (e.g., `history_to_use = self.voltage_history[:t_neuron_idx+1]`).")
print("However, your current implementation is a pragmatic choice to cap the history for performance.")

print(f"\nAverage time for one individual `np.dot` call (across all neurons, all updates): {(total_frac_dot_time_overall / num_neuron_updates_total if num_neuron_updates_total > 0 else 0) * 1e6:.3f} µs")
print(f"Average time for one individual `np.roll` call (across all neurons, all updates): {(total_frac_roll_time_overall / num_neuron_updates_total if num_neuron_updates_total > 0 else 0) * 1e6:.3f} µs")


# --- Hardware Comparison Section (to be filled by you) ---
print("\n--- Hardware vs. Emulation Speed Comparison ---")
print("To complete this comparison, you will need to provide the following data based on your SPICE simulations and communication estimates:")
print("1. **T_compute_device_us:** Estimated average time for the *entire 8-neuron network* to make *one Santa Fe Trail decision* on your analog hardware (e.g., 50-500 µs).")
print("2. **T_comm_us:** Estimated average time for *one round-trip* of communication (send inputs + receive outputs) between your main controller and your analog device (e.g., 50-500 µs).")

print("\nOnce you have these values, you can plug them into the following conceptual calculation:")
print("   Total Hardware Decision Time (per Ant Step) = T_compute_device_us + T_comm_us")
print("   Speedup Factor = (Average Python Time for ALL Neuron Updates per Ant Step) / (Total Hardware Decision Time)")
print("\nThen, we can discuss the precise numerical speedup.")
