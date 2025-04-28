// reservoir.v
// Liquid State Machine Reservoir
// 64 LIF neurons, sparse connectivity, 16-bit signed fixed-point (Q4.12)
// Fixed random internal weights (W) and input weights (W_in)

module reservoir (
    input wire clk,
    input wire reset,
    input wire signed [15:0] input_signal,   // External input (fixed-point Q4.12)
    output reg [63:0] spikes_out              // Spike outputs
);

    // Parameters
    parameter integer N = 64;
    parameter signed [15:0] threshold = 16'sd2048; // 0.5 in Q4.12
    parameter signed [15:0] leak_mul = 16'sd3686; // ~0.9 in Q4.12 (0.9 * 4096 = 3686)
    parameter integer refractory_period = 2;

    // Internal states
    reg signed [15:0] membrane_potential [0:N-1];
    reg [1:0] refractory_counter [0:N-1];
    reg signed [15:0] W_in [0:N-1];
    reg signed [15:0] W [0:N-1][0:N-1];

    integer i, j;

    // Initialize weights
    initial begin
        // Example W_in values (replace with generated ones)
        W_in[0] = 16'sd512; W_in[1] = 16'sd1024; /* etc... */
        // Example W values (replace with generated ones)
        W[0][0] = 16'sd0; W[0][1] = 16'sd500; /* etc... */
        // (I'll paste the full real generated weights next!)
    end

    // Reservoir dynamics
    always @(posedge clk or posedge reset) begin
        if (reset) begin
            for (i = 0; i < N; i = i + 1) begin
                membrane_potential[i] <= 16'sd0;
                refractory_counter[i] <= 2'd0;
                spikes_out[i] <= 1'b0;
            end
        end else begin
            reg signed [31:0] total_input [0:N-1];  // 32 bits to avoid overflow

            // 1. Sum recurrent inputs
            for (i = 0; i < N; i = i + 1) begin
                total_input[i] = $signed(W_in[i]) * $signed(input_signal);  // input contribution
                for (j = 0; j < N; j = j + 1) begin
                    if (spikes_out[j]) begin
                        total_input[i] = total_input[i] + $signed(W[i][j]);
                    end
                end
            end

            // 2. Update each neuron
            for (i = 0; i < N; i = i + 1) begin
                if (refractory_counter[i] != 0) begin
                    refractory_counter[i] <= refractory_counter[i] - 1;
                    spikes_out[i] <= 1'b0;
                end else begin
                    // Leak potential
                    membrane_potential[i] <= (membrane_potential[i] * leak_mul) >>> 12;
                    // Add input
                    membrane_potential[i] <= membrane_potential[i] + total_input[i][15:0];
                    // Check for spike
                    if (membrane_potential[i] > threshold) begin
                        spikes_out[i] <= 1'b1;
                        membrane_potential[i] <= 16'sd0;
                        refractory_counter[i] <= refractory_period;
                    end else begin
                        spikes_out[i] <= 1'b0;
                    end
                end
            end
        end
    end

endmodule

