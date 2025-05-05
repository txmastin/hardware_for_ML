# Feedforward Neural Network Benchmark

Benchmark of a 2-layer feedforward neural network with ReLU activations.

## Configuration

- Batch sizes: 100 and 10,000
- Input sizes: 100 and 1,000
- Architecture: Input → 128 → 128 → Output (10)
- Operation: Forward pass only

## Methods Compared

- PyTorch (GPU)
- CUDA (cuBLAS + custom ReLU kernel)
- C with OpenBLAS (CPU)

## Results

### Input size = 100, batch size = 1000

| Method       | Time (ms)  |
|--------------|------------|
| OpenBLAS C   | 5.0840     |
| CUDA         | 65.5952    |
| PyTorch      | 81.2111    |

### Input size = 1000, batch size = 1000

| Method       | Time (ms)  |
|--------------|------------|
| PyTorch      | 4.2114     |
| CUDA         | 6.4046     |
| OpenBLAS C   | 36.2370    |

## Observations

- For small inputs and batch sizes, OpenBLAS was fastest due to minimal overhead.
- For large inputs and batches, PyTorch and CUDA outperformed OpenBLAS significantly.
- PyTorch was the fastest overall at large scale, benefiting from cuDNN and cuBLAS optimizations.
- The CUDA implementation scaled well, with moderate overhead from manual memory management and kernel launches.
- OpenBLAS became significantly slower at large scale due to CPU memory limitations and lack of parallel execution.

