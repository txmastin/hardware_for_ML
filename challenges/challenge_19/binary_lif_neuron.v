module binary_lif_neuron #(
    parameter WIDTH = 8,
    parameter THRESHOLD = 5,
    parameter RESET_VAL = 0,
    parameter LEAK_NUM = 9,
    parameter LEAK_DEN = 10
)(
    input wire clk,
    input wire rst,
    input wire in,
    output reg spike,
    output reg [WIDTH-1:0] potential
);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            potential <= 0;
            spike <= 0;
        end else begin
            // Apply leak
            potential <= (potential * LEAK_NUM) / LEAK_DEN;

            // Accumulate input
            if (in)
                potential <= potential + 1;

            // Spike check based on updated potential
            if (potential >= THRESHOLD) begin
                spike <= 1;
                potential <= RESET_VAL;
            end else begin
                spike <= 0;
            end
        end
    end
endmodule

