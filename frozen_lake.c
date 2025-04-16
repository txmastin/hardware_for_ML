#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

#define GRID_SIZE 4
#define STATE_COUNT 16
#define ACTION_COUNT 4

#define START_STATE 0
#define HOLE 2
#define GOAL 3

// Action deltas: left, down, right, up
int dr[] = {0, 1, 0, -1};
int dc[] = {-1, 0, 1, 0};

int lake[GRID_SIZE][GRID_SIZE] = {
    {0, 1, 1, 1},
    {1, 2, 1, 2},
    {1, 1, 1, 2},
    {2, 1, 1, 3}
};

double Q[STATE_COUNT][ACTION_COUNT];

int coords_to_state(int r, int c) {
    return r * GRID_SIZE + c;
}

void state_to_coords(int s, int* r, int* c) {
    *r = s / GRID_SIZE;
    *c = s % GRID_SIZE;
}

int is_terminal(int s) {
    int r, c;
    state_to_coords(s, &r, &c);
    int tile = lake[r][c];
    return tile == HOLE || tile == GOAL;
}

int step(int state, int action, int* reward, int* done) {
    int r, c;
    state_to_coords(state, &r, &c);
    int nr = r + dr[action];
    int nc = c + dc[action];

    // stay in place if out of bounds
    if (nr < 0 || nr >= GRID_SIZE || nc < 0 || nc >= GRID_SIZE)
        nr = r, nc = c;

    int new_state = coords_to_state(nr, nc);
    int tile = lake[nr][nc];

    *reward = (tile == GOAL) ? 1 : 0;
    *done = (tile == HOLE || tile == GOAL);
    return new_state;
}

int main() {
    srand(time(NULL));

    // Hyperparameters
    int episodes = 2000;
    double alpha = 0.8;
    double gamma = 0.95;
    double epsilon = 1.0;
    double epsilon_min = 0.01;
    double decay = 0.001;

    clock_t start_time = clock();

    for (int ep = 0; ep < episodes; ep++) {
        int state = START_STATE;
        int done = 0;

        while (!done) {
            int action;
            if ((double)rand() / RAND_MAX < epsilon) {
                action = rand() % ACTION_COUNT;
            } else {
                // argmax Q[state]
                action = 0;
                for (int a = 1; a < ACTION_COUNT; a++) {
                    if (Q[state][a] > Q[state][action])
                        action = a;
                }
            }

            int reward, next_done;
            int new_state = step(state, action, &reward, &next_done);

            // Q update
            double max_q_next = Q[new_state][0];
            for (int a = 1; a < ACTION_COUNT; a++) {
                if (Q[new_state][a] > max_q_next)
                    max_q_next = Q[new_state][a];
            }

            Q[state][action] = Q[state][action] * (1 - alpha) + alpha * (reward + gamma * max_q_next);
            state = new_state;
            done = next_done;
        }

        // Decay epsilon
        epsilon = fmax(epsilon_min, epsilon * exp(-decay));
    }

    clock_t end_time = clock();
    double elapsed_sec = (double)(end_time - start_time) / CLOCKS_PER_SEC;
    printf("Training completed in %.4f seconds\n\n", elapsed_sec);

    // Print policy
    char* action_chars[] = {"←", "↓", "→", "↑"};
    for (int s = 0; s < STATE_COUNT; s++) {
        int r, c;
        state_to_coords(s, &r, &c);
        int tile = lake[r][c];

        if (tile == HOLE) printf(" H ");
        else if (tile == GOAL) printf(" G ");
        else {
            int best = 0;
            for (int a = 1; a < ACTION_COUNT; a++) {
                if (Q[s][a] > Q[s][best])
                    best = a;
            }
            printf(" %s ", action_chars[best]);
        }

        if ((s + 1) % GRID_SIZE == 0) printf("\n");
    }

    return 0;
}

