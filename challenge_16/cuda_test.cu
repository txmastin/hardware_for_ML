
#include <stdio.h>
#include <stdlib.h>
#include <cuda_runtime.h>
#include <cublas_v2.h>
#include <time.h>

#define BATCH 100
#define IN 100
#define HIDDEN 128
#define OUT 10

__global__ void relu_kernel(float* x, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N)
        x[i] = fmaxf(x[i], 0.0f);
}

void check(cudaError_t status, const char* msg) {
    if (status != cudaSuccess) {
        fprintf(stderr, "%s: %s\n", msg, cudaGetErrorString(status));
        exit(EXIT_FAILURE);
    }
}

int main() {
    float *input, *w1, *w2, *hidden, *output;
    float *d_input, *d_w1, *d_w2, *d_hidden, *d_output;
    cublasHandle_t handle;
    cudaEvent_t start, stop;

    input = (float*)malloc(BATCH * IN * sizeof(float));
    w1 = (float*)malloc(IN * HIDDEN * sizeof(float));
    w2 = (float*)malloc(HIDDEN * OUT * sizeof(float));
    hidden = (float*)malloc(BATCH * HIDDEN * sizeof(float));
    output = (float*)malloc(BATCH * OUT * sizeof(float));

    for (int i = 0; i < BATCH * IN; i++) input[i] = 1.0f;
    for (int i = 0; i < IN * HIDDEN; i++) w1[i] = 0.01f;
    for (int i = 0; i < HIDDEN * OUT; i++) w2[i] = 0.01f;

    check(cudaMalloc(&d_input, BATCH * IN * sizeof(float)), "cudaMalloc input");
    check(cudaMalloc(&d_w1, IN * HIDDEN * sizeof(float)), "cudaMalloc w1");
    check(cudaMalloc(&d_w2, HIDDEN * OUT * sizeof(float)), "cudaMalloc w2");
    check(cudaMalloc(&d_hidden, BATCH * HIDDEN * sizeof(float)), "cudaMalloc hidden");
    check(cudaMalloc(&d_output, BATCH * OUT * sizeof(float)), "cudaMalloc output");

    check(cudaMemcpy(d_input, input, BATCH * IN * sizeof(float), cudaMemcpyHostToDevice), "copy input");
    check(cudaMemcpy(d_w1, w1, IN * HIDDEN * sizeof(float), cudaMemcpyHostToDevice), "copy w1");
    check(cudaMemcpy(d_w2, w2, HIDDEN * OUT * sizeof(float), cudaMemcpyHostToDevice), "copy w2");

    cublasCreate(&handle);
    float alpha = 1.0f, beta = 0.0f;

    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start);

    // Forward 1: input @ w1
    cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, HIDDEN, BATCH, IN,
                &alpha, d_w1, HIDDEN, d_input, IN, &beta, d_hidden, HIDDEN);
    relu_kernel<<<(BATCH*HIDDEN + 255)/256, 256>>>(d_hidden, BATCH * HIDDEN);

    // Forward 2: hidden @ w2
    cublasSgemm(handle, CUBLAS_OP_N, CUBLAS_OP_N, OUT, BATCH, HIDDEN,
                &alpha, d_w2, OUT, d_hidden, HIDDEN, &beta, d_output, OUT);

    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float ms = 0;
    cudaEventElapsedTime(&ms, start, stop);
    printf("CUDA Time: %.4f ms\n", ms);

    cudaFree(d_input); cudaFree(d_w1); cudaFree(d_w2);
    cudaFree(d_hidden); cudaFree(d_output);
    free(input); free(w1); free(w2); free(hidden); free(output);
    cublasDestroy(handle);
    return 0;
}
