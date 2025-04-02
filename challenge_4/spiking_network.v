module spiking_network #(
    parameter N_INPUT = 4,
    parameter N_OUTPUT = 3,
    parameter WEIGHT_WIDTH = 8,
    parameter CURRENT_WIDTH = 8
)(
    input wire clk,
    input wire rst,
    input wire signed [CURRENT_WIDTH-1:0] input_current [N_INPUT-1:0],
    output wire output_spikes [N_OUTPUT-1:0]
);

    // === Internal spike wires ===
    wire input_spikes [N_INPUT-1:0];
    wire signed [CURRENT_WIDTH-1:0] layer1_current [N_OUTPUT-1:0];

    // === Synaptic weight matrix: Layer0 -> Layer1 ===
    reg signed [WEIGHT_WIDTH-1:0] synapse [0:N_OUTPUT-1][0:N_INPUT-1];

    // === Instantiate input neurons ===
    genvar i;
    generate
        for (i = 0; i < N_INPUT; i = i + 1) begin : input_neurons
            lif_neuron input_neuron_inst (
                .clk(clk),
                .rst(rst),
                .input_current(input_current[i]),
                .spike(input_spikes[i])
            );
        end
    endgenerate

    // === Weighted sum of input spikes ===
    integer jj, k;
    always @(*) begin
        for (jj = 0; jj < N_OUTPUT; jj = jj + 1) begin
            layer1_current[jj] = 0;
            for (k = 0; k < N_INPUT; k = k + 1) begin
                if (input_spikes[k])
                    layer1_current[jj] = layer1_current[jj] + synapse[jj][k];
            end
        end
    end

    // === Instantiate output neurons ===
    genvar j; 
    generate
        for (j = 0; j < N_OUTPUT; j = j + 1) begin : output_neurons
            lif_neuron output_neuron_inst (
                .clk(clk),
                .rst(rst),
                .input_current(layer1_current[j]),
                .spike(output_spikes[j])
            );
        end
    endgenerate

    // === Example: initialize synapses manually ===
    initial begin
        // Synapse[i][j] is weight from input j to output i
        synapse[0][0] = 5; synapse[0][1] = -3; synapse[0][2] = 2; synapse[0][3] = 1;
        synapse[1][0] = -2; synapse[1][1] = 4; synapse[1][2] = 3; synapse[1][3] = -1;
        synapse[2][0] = 1; synapse[2][1] = 1; synapse[2][2] = 1; synapse[2][3] = 1;
    end

endmodule

