import numpy as np

# Map representation
lake = np.array([
    [0, 1, 1, 1],
    [1, 2, 1, 2],
    [1, 1, 1, 2],
    [2, 1, 1, 3]
])

state_to_coords = lambda s: (s // 4, s % 4)
coords_to_state = lambda r, c: r * 4 + c

# Action mapping: 0=left, 1=down, 2=right, 3=up
actions = [(-0, -1), (1, 0), (0, 1), (-1, 0)]
n_states = 16
n_actions = 4

# Initialize Q-table
Q = np.zeros((n_states, n_actions))

# Hyperparameters
episodes = 2000
alpha = 0.8
gamma = 0.95
epsilon = 1.0
epsilon_min = 0.01
decay = 0.001

def is_terminal(s):
    r, c = state_to_coords(s)
    return lake[r, c] in [2, 3]  # hole or goal

def step(state, action):
    r, c = state_to_coords(state)
    dr, dc = actions[action]
    nr, nc = r + dr, c + dc

    # Check bounds
    if 0 <= nr < 4 and 0 <= nc < 4:
        new_state = coords_to_state(nr, nc)
    else:
        new_state = state  # bump into wall

    tile = lake[state_to_coords(new_state)]
    reward = 1 if tile == 3 else 0
    done = tile in [2, 3]
    return new_state, reward, done

# Q-learning main loop

import time

start_time = time.time()

# Q-learning training loop
for episode in range(episodes):
    state = 0  # always start at S
    done = False

    while not done:
        if np.random.rand() < epsilon:
            action = np.random.randint(n_actions)
        else:
            action = np.argmax(Q[state])

        new_state, reward, done = step(state, action)
        Q[state, action] = Q[state, action] * (1 - alpha) + \
            alpha * (reward + gamma * np.max(Q[new_state]))
        state = new_state

    epsilon = max(epsilon_min, epsilon * np.exp(-decay))

end_time = time.time()
print(f"\nTraining completed in {end_time - start_time:.4f} seconds")

np.set_printoptions(precision=2, suppress=True)
print(Q)

# Show the final policy
actions_symbols = ['←', '↓', '→', '↑']
policy = np.full((4, 4), ' ')
for s in range(n_states):
    if is_terminal(s):
        policy[state_to_coords(s)] = 'H' if lake[state_to_coords(s)] == 2 else 'G'
    else:
        best_action = np.argmax(Q[s])
        policy[state_to_coords(s)] = actions_symbols[best_action]

print("\nFinal policy:")
for row in policy:
    print(' '.join(row))

