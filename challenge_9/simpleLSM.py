import numpy as np
import time
import matplotlib.pyplot as plt

class SpikingLiquidStateMachine:
    def __init__(self, 
                 n_reservoir=1000, 
                 connectivity=0.2, 
                 spectral_radius=0.9, 
                 input_scaling=0.115, 
                 leak_rate=0.2, 
                 threshold=0.5, 
                 resting_potential=0.0, 
                 refractory_period=2):
        
        self.n_reservoir = n_reservoir
        self.connectivity = connectivity
        self.spectral_radius = spectral_radius
        self.input_scaling = input_scaling
        self.leak_rate = leak_rate
        self.threshold = threshold
        self.resting_potential = resting_potential
        self.refractory_period = refractory_period

        # Initialize reservoir weights
        self.W = np.random.rand(n_reservoir, n_reservoir)
        self.W[np.random.rand(*self.W.shape) > connectivity] = 0
        self.W = self.W - np.diag(np.diag(self.W))  # Remove self-connections
        self.W = self.W / np.max(np.abs(np.linalg.eigvals(self.W))) * spectral_radius

        # Initialize input weights
        self.W_in = np.random.rand(n_reservoir) 
        
        # Initialize output weights        
        self.W_out = np.random.rand(1, n_reservoir)

        self.W_out[:][np.random.rand(*self.W_out.shape) > connectivity] = 0
        
        # Initialize neuron states
        self.neuron_states = np.zeros(n_reservoir)
        self.neuron_spikes = np.zeros(n_reservoir)
        self.fired = np.zeros(n_reservoir, dtype=bool)
        self.refractory_counters = np.zeros(n_reservoir, dtype=int)
    
        self.neuron_spikes_prev = np.zeros(n_reservoir)

    def step(self, input_signal):
        self.neuron_spikes = self.fired.astype(int) 
        total_input = np.dot(self.W, self.neuron_spikes) + self.W_in * input_signal * self.input_scaling

        # Refractory handling: block input accumulation for refractory neurons
        refractory_mask = self.refractory_counters > 0
        total_input[refractory_mask] = 0

        # Update neuron states with leak and input
        self.neuron_states = (1 - self.leak_rate) * self.neuron_states + total_input

        # Detect spiking neurons
        self.fired = self.neuron_states > self.threshold
        self.neuron_states[self.fired] = self.resting_potential

        self.refractory_counters[self.fired] = self.refractory_period

        # Reduce refractory counters
        self.refractory_counters[refractory_mask] -= 1
        return self.neuron_states, sum(self.fired)

    def predict(self, reservoir_activations):
        return np.dot(self.W_out, reservoir_activations)
        #return (np.tanh(np.dot(self.W_out, reservoir_activations)) + 1) / 2


def train_output_layer(lsm, input_sequence, target, learning_rate):
    printing = False
    for value in input_sequence: 
        reservoir_activations, avl = lsm.step(value)
    prediction = lsm.predict(reservoir_activations)
    
    error = target - prediction
    if printing:
        print("target:", target, "\nprediction", prediction)
        print("error:", error)

    #norm_activations = reservoir_activations / (np.linalg.norm(reservoir_activations) + 1e-6)
    lsm.W_out += learning_rate * np.outer(error, reservoir_activations)
    return abs(error), prediction

def test_output_layer(lsm, input_sequence, target): #target is now a single value
    printing = False
    largest = 0
    for value in input_sequence:
        reservoir_activations, avl = lsm.step(value) 
        if avl > largest:
            largest = avl
    
    prediction = lsm.predict(reservoir_activations)
    
    error = target - prediction
    print(largest)

    if printing:
        print("target:", target, "\nprediction", prediction)
        print("error:", error)

    return error, prediction


def training_loop(lsm, num_epochs, input_window_size, inp, learning_rate):
    avg_errors = []
    final_out = []
    for epoch in range(num_epochs):
        epoch_error = []
        for i in range(len(inp) - input_window_size):
            input_sequence = inp[i:i+input_window_size]
            target = inp[i + input_window_size]
            err, out = train_output_layer(lsm, input_sequence, target, learning_rate)
            epoch_error.append(err)
            if epoch == num_epochs - 1:
                final_out.append(out)

        avg_errors.append(np.mean(epoch_error))
        if(epoch % 2 == 0):
            print(f"Training Step: {epoch}/{num_epochs}, Average Error: {np.mean(epoch_error)}")
    return avg_errors, final_out


def benchmark_lsm(lsm, num_epochs, input_window_size, input_signal, learning_rate):
    print(f"\nBenchmarking LSM")
    print(f"- Reservoir size: {lsm.n_reservoir}")
    print(f"- Input window size: {input_window_size}")
    print(f"- Training epochs: {num_epochs}")
    print(f"- Total steps: {num_epochs * (len(input_signal) - input_window_size)}")

    # Time training
    print("\nMeasuring training time...")
    start_train = time.time()
    avg_errors, _ = training_loop(lsm, num_epochs, input_window_size, input_signal, learning_rate)
    end_train = time.time()
    train_time = end_train - start_train

    # Time step()
    print("Measuring average step() time...")
    num_test_steps = 10000
    dummy_input = np.random.rand()
    start_step = time.time()
    for _ in range(num_test_steps):
        lsm.step(dummy_input)
    end_step = time.time()
    step_time = (end_step - start_step) / num_test_steps

    print("\nBenchmark Report:")
    print(f"- Total training time: {train_time:.4f} seconds")
    print(f"- Avg time per epoch: {train_time / num_epochs:.6f} seconds")
    print(f"- Avg time per step(): {step_time * 1e6:.2f} µs")
    print(f"- Final training error: {avg_errors[-1]:.6f}")

    return {
        "reservoir_size": lsm.n_reservoir,
        "train_time_sec": train_time,
        "step_time_sec": step_time,
        "final_error": avg_errors[-1]
    }



with open("datasets/MG/mgdata.dat.txt", 'r') as file:
    lines = file.readlines()

mg = [float(line.split()[1]) for line in lines]


N = 64
lsm_critical = SpikingLiquidStateMachine(n_reservoir=N, input_scaling=0.105) 
num_epochs = 500
input_window_size = 5 
learning_rate = 0.001

benchmark_lsm(lsm_critical, num_epochs, input_window_size, mg, learning_rate)
'''
avg_errors_critical, _ = training_loop(lsm_critical, num_epochs, input_window_size, mg, learning_rate)

plt.figure()
plt.plot(avg_errors_critical, color="red", label="Critical Spiking")
'''
