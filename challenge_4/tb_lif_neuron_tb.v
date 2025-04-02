`timescale 1ns/1ps

module tb_lif_neuron;

    // Parameters
    parameter WIDTH = 16;
    parameter THRESHOLD = 20;
    parameter DECAY = 1;
    parameter REF_PERIOD = 5;

    // Signals
    reg clk;
    reg rst;
    reg signed [7:0] input_current;
    wire spike;

    // Instantiate neuron
    lif_neuron #(
        .WIDTH(WIDTH),
        .THRESHOLD(THRESHOLD),
        .DECAY(DECAY),
        .REF_PERIOD(REF_PERIOD)
    ) neuron (
        .clk(clk),
        .rst(rst),
        .input_current(input_current),
        .spike(spike)
    );

    // Clock generation
    always #5 clk = ~clk;  // 100 MHz clock

    initial begin
        $display("Starting LIF neuron test...");
        $dumpfile("lif_neuron.vcd");
        $dumpvars(0, tb_lif_neuron);

        // Initialize
        clk = 0;
        rst = 1;
        input_current = 0;
        #10;

        // Release reset
        rst = 0;
        input_current = 5;

        // Run enough time to reach threshold and spike
        repeat (10) begin
            #10;
        end

        // After spike, input still applied, should ignore input during ref
        repeat (10) begin
            #10;
        end

        // Apply negative current (inhibition)
        input_current = -5;
        repeat (5) begin
            #10;
        end

        // Apply a large positive current for fast spike
        input_current = 25;
        repeat (5) begin
            #10;
        end

        $display("Test complete.");
        $finish;
    end
endmodule

