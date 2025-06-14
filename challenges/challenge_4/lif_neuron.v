module lif_neuron #(
    parameter WIDTH = 16,               // Membrane potential width
    parameter THRESHOLD = 100,          // Spike threshold
    parameter DECAY = 1,                // Leak per time step
    parameter REF_PERIOD = 10           // Refractory period length
)(
    input wire clk,
    input wire rst,
    input wire signed [7:0] input_current,
    output reg spike
);

    reg signed [WIDTH-1:0] V_mem = 0;
    reg [$clog2(REF_PERIOD+1)-1:0] ref_count = 0;

    wire in_refractory = (ref_count != 0);

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            V_mem <= 0;
            spike <= 0;
            ref_count <= 0;
        end else begin
            if (in_refractory) begin
                // Count down refractory period
                ref_count <= ref_count - 1;
                spike <= 0;
            end else begin
                // Integrate input current and apply decay
                V_mem <= V_mem + input_current - DECAY;

                if (V_mem >= THRESHOLD) begin
                    spike <= 1;
                    V_mem <= 0;
                    ref_count <= REF_PERIOD;
                end else begin
                    spike <= 0;
                end
            end
        end
    end
endmodule
