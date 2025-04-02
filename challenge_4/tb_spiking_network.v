`timescale 1ns/1ps

module tb_spiking_network;

    parameter N_INPUT = 4;
    parameter N_OUTPUT = 3;
    parameter CYCLE = 10;

    reg clk;
    reg rst;
    reg signed [7:0] input_current [N_INPUT-1:0];
    wire output_spikes [N_OUTPUT-1:0];

    // Instantiate the network
    spiking_network #(
        .N_INPUT(N_INPUT),
        .N_OUTPUT(N_OUTPUT)
    ) net (
        .clk(clk),
        .rst(rst),
        .input_current(input_current),
        .output_spikes(output_spikes)
    );

    // Clock generation
    always #(CYCLE/2) clk = ~clk;

    integer t;
    initial begin
        $dumpfile("spiking_network.vcd");
        $dumpvars(0, tb_spiking_network);

        // Initialize
        clk = 0;
        rst = 1;
        for (t = 0; t < N_INPUT; t = t + 1)
            input_current[t] = 0;

        #CYCLE;
        rst = 0;

        // === Apply a current strong enough to cause spikes in some input neurons ===
        input_current[0] = 20; // should integrate and spike
        input_current[1] = 0;
        input_current[2] = 10;
        input_current[3] = 0;

        // Run for several cycles to allow spikes to propagate
        repeat (20) begin
            #CYCLE;
        end

        // Turn off current to test decay and stop firing
        input_current[0] = 0;
        input_current[2] = 0;

        repeat (20) begin
            #CYCLE;
        end

        $display("Test complete.");
        $finish;
    end
endmodule

