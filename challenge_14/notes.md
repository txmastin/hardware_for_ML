**CPU** (sequential loop): *1.0000 ms*

    - Very fast, likely due to cache locality and minimal branching

    - Outperforms naive GPU implementation due to low overhead and efficient scalar execution

**GPU** (linear, single thread): *16.2324 ms*

    - Significantly slower than CPU

    - Likely bottlenecked by memory latency and doesn't benefit from any parallelisation on the device

**GPU** (parallel matrix exponentiation): *0.606432 ms*

    - Very fast, nearly 2x faster than CPU and over 25× faster than linear GPU

    - Each thread independently computes F(n) using fast doubling via matrix exponentiation

    - Excellent speedup due to high parallel occupancy and no inter-thread dependencies


