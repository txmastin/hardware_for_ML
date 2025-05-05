#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <cblas.h>

#define INPUT_SIZE 100
#define HIDDEN_SIZE 128
#define OUTPUT_SIZE 10
#define NUM_SAMPLES 100

// ReLU activation
void relu_vec(float *vec, int size) {
    for (int i = 0; i < size; i++) {
        if (vec[i] < 0) vec[i] = 0;
    }
}

// Fill a matrix with random values
void random_init(float *matrix, int rows, int cols) {
    for (int i = 0; i < rows * cols; i++) {
        matrix[i] = ((float)rand() / RAND_MAX) * 2.0f - 1.0f; // Random between -1 and 1
    }
}

// Fill a vector with random values
void random_vec(float *vec, int size) {
    for (int i = 0; i < size; i++) {
        vec[i] = ((float)rand() / RAND_MAX) * 2.0f - 1.0f;
    }
}

int main() {
    srand(time(NULL));

    // Allocate memory
    float input[NUM_SAMPLES][INPUT_SIZE];
    float hidden1[HIDDEN_SIZE];
    float hidden2[HIDDEN_SIZE];
    float output[OUTPUT_SIZE];

    float W1[HIDDEN_SIZE * INPUT_SIZE];
    float W2[HIDDEN_SIZE * HIDDEN_SIZE];
    float W3[OUTPUT_SIZE * HIDDEN_SIZE];

    random_init(W1, HIDDEN_SIZE, INPUT_SIZE);
    random_init(W2, HIDDEN_SIZE, HIDDEN_SIZE);
    random_init(W3, OUTPUT_SIZE, HIDDEN_SIZE);

    for (int n = 0; n < NUM_SAMPLES; n++) {
        random_vec(input[n], INPUT_SIZE);
    }

    clock_t start = clock();
    for (int i = 0; i < 1; i++) {
        for (int n = 0; n < NUM_SAMPLES; n++) {
            // hidden1 = W1 * input
            cblas_sgemv(CblasRowMajor, CblasNoTrans,
                        HIDDEN_SIZE, INPUT_SIZE,
                        1.0f, W1, INPUT_SIZE,
                        input[n], 1,
                        0.0f, hidden1, 1);

            relu_vec(hidden1, HIDDEN_SIZE);

            // hidden2 = W2 * hidden1
            cblas_sgemv(CblasRowMajor, CblasNoTrans,
                        HIDDEN_SIZE, HIDDEN_SIZE,
                        1.0f, W2, HIDDEN_SIZE,
                        hidden1, 1,
                        0.0f, hidden2, 1);

            relu_vec(hidden2, HIDDEN_SIZE);

            // output = W3 * hidden2
            cblas_sgemv(CblasRowMajor, CblasNoTrans,
                        OUTPUT_SIZE, HIDDEN_SIZE,
                        1.0f, W3, HIDDEN_SIZE,
                        hidden2, 1,
                        0.0f, output, 1);
            // No ReLU at the output
        }
    }
    clock_t end = clock();

    double elapsed = (double)(end - start) / CLOCKS_PER_SEC * 1000.0; // milliseconds

    printf("OpenBLAS C forward time: %.4f ms\n", elapsed);

    return 0;
}

