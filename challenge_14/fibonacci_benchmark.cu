
#include <iostream>
#include <vector>
#include <chrono>
#include <cuda.h>

#define N (1 << 20)

void fibonacci_cpu(std::vector<unsigned long long>& fib, int n) {
    fib[0] = 0;
    fib[1] = 1;
    for (int i = 2; i < n; ++i) {
        fib[i] = fib[i - 1] + fib[i - 2];
    }
}

__global__ void fibonacci_gpu_linear(unsigned long long* fib, int n) {
    if (threadIdx.x == 0 && blockIdx.x == 0) {
        fib[0] = 0;
        fib[1] = 1;
        for (int i = 2; i < n; ++i) {
            fib[i] = fib[i - 1] + fib[i - 2];
        }
    }
}

__device__ void mat_mult(unsigned long long a[2][2], unsigned long long b[2][2], unsigned long long res[2][2]) {
    res[0][0] = a[0][0]*b[0][0] + a[0][1]*b[1][0];
    res[0][1] = a[0][0]*b[0][1] + a[0][1]*b[1][1];
    res[1][0] = a[1][0]*b[0][0] + a[1][1]*b[1][0];
    res[1][1] = a[1][0]*b[0][1] + a[1][1]*b[1][1];
}

__device__ void mat_pow(unsigned long long base[2][2], int n, unsigned long long res[2][2]) {
    res[0][0] = 1; res[0][1] = 0;
    res[1][0] = 0; res[1][1] = 1;

    unsigned long long temp[2][2];
    while (n > 0) {
        if (n & 1) {
            mat_mult(res, base, temp);
            res[0][0] = temp[0][0]; res[0][1] = temp[0][1];
            res[1][0] = temp[1][0]; res[1][1] = temp[1][1];
        }
        mat_mult(base, base, temp);
        base[0][0] = temp[0][0]; base[0][1] = temp[0][1];
        base[1][0] = temp[1][0]; base[1][1] = temp[1][1];
        n >>= 1;
    }
}

__global__ void fibonacci_gpu_parallel(unsigned long long* out, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= n) return;

    if (idx == 0) {
        out[0] = 0;
        return;
    }
    if (idx == 1) {
        out[1] = 1;
        return;
    }

    unsigned long long base[2][2] = {{1, 1}, {1, 0}};
    unsigned long long res[2][2];
    mat_pow(base, idx - 1, res);
    out[idx] = res[0][0];
}

void check_correctness(const std::vector<unsigned long long>& a, const std::vector<unsigned long long>& b) {
    for (int i = 0; i < 100; ++i) {
        if (a[i] != b[i]) {
            std::cerr << "Mismatch at index " << i << ": CPU=" << a[i] << ", GPU=" << b[i] << "\n";
            return;
        }
    }
    std::cout << "Results match (first 100 elements).\n";
}

int main() {
    std::vector<unsigned long long> fib_cpu(N);

    // ---------------- CPU ----------------
    auto start_cpu = std::chrono::high_resolution_clock::now();
    fibonacci_cpu(fib_cpu, N);
    auto end_cpu = std::chrono::high_resolution_clock::now();
    std::cout << "CPU Time: "
              << std::chrono::duration_cast<std::chrono::milliseconds>(end_cpu - start_cpu).count()
              << " ms\n";

    // ---------------- GPU Linear ----------------
    unsigned long long* d_fib;
    cudaMalloc(&d_fib, N * sizeof(unsigned long long));
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    fibonacci_gpu_linear<<<1, 1>>>(d_fib, N);
    cudaDeviceSynchronize();  
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess)
      std::cerr << "CUDA Error: " << cudaGetErrorString(err) << std::endl;

    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float ms_linear = 0;
    cudaEventElapsedTime(&ms_linear, start, stop);
    std::cout << "GPU Linear Time: " << ms_linear << " ms\n";

    std::vector<unsigned long long> fib_gpu_linear(N);
    cudaMemcpy(fib_gpu_linear.data(), d_fib, N * sizeof(unsigned long long), cudaMemcpyDeviceToHost);
    check_correctness(fib_cpu, fib_gpu_linear);

    // ---------------- GPU Parallel Matrix ----------------
    int threads = 256;
    int blocks = (N + threads - 1) / threads;

    cudaEventRecord(start);
    fibonacci_gpu_parallel<<<blocks, threads>>>(d_fib, N);
    cudaDeviceSynchronize();  
    err = cudaGetLastError();
    if (err != cudaSuccess)
      std::cerr << "CUDA Error: " << cudaGetErrorString(err) << std::endl;

    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float ms_parallel = 0;
    cudaEventElapsedTime(&ms_parallel, start, stop);
    std::cout << "GPU Parallel Matrix Time: " << ms_parallel << " ms\n";

    std::vector<unsigned long long> fib_gpu_parallel(N);
    cudaMemcpy(fib_gpu_parallel.data(), d_fib, N * sizeof(unsigned long long), cudaMemcpyDeviceToHost);
    check_correctness(fib_cpu, fib_gpu_parallel);

    // Cleanup
    cudaFree(d_fib);
    cudaEventDestroy(start);
    cudaEventDestroy(stop);
    return 0;
}
