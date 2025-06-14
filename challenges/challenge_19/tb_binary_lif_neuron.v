`timescale 1ns / 1ps

module tb_binary_lif_neuron;
    reg clk = 0;
    reg rst = 1;
    reg in;
    wire spike;
    wire [7:0] potential;

    binary_lif_neuron #(
        .WIDTH(8),
        .THRESHOLD(5),
        .RESET_VAL(0),
        .LEAK_NUM(90),
        .LEAK_DEN(100)
    ) dut (
        .clk(clk),
        .rst(rst),
        .in(in),
        .spike(spike),
        .potential(potential)
    );

    always #5 clk = ~clk; // 10ns clock

    initial begin
        // Reset
        #10 rst = 0;

        // -----------------------------
        // Scenario 1: Constant input below threshold
        // -----------------------------
        $display("\n--- Scenario 1: Constant input below threshold ---\n");
        $display("\nTime\tIn\t  V\tSpike");
        in = 0;
        repeat(10) begin
            @(posedge clk);
            $display("%g\t%b\t%d\t%b", $time, in, potential, spike);
        end

        // -----------------------------
        // Scenario 2: Input accumulates to threshold and spikes
        // -----------------------------
        $display("\n--- Scenario 2: Accumulating input until spike ---\n");
        $display("\nTime\tIn\t  V\tSpike");
        in = 1;
        repeat(6) begin
            @(posedge clk);
            $display("%g\t%b\t%d\t%b", $time, in, potential, spike);
        end

        // -----------------------------
        // Scenario 3: Leakage with no input
        // -----------------------------
        $display("\n--- Scenario 3: Leakage with no input ---\n");
        $display("\nTime\tIn\t  V\tSpike");
        in = 1;
        repeat(3) begin
            @(posedge clk);
            $display("%g\t%b\t%d\t%b", $time, in, potential, spike);
        end

        in = 0;
        repeat(10) begin
            @(posedge clk);
            $display("%g\t%b\t%d\t%b", $time, in, potential, spike);
        end

        // -----------------------------
        // Scenario 4: Strong input causes immediate spike
        // -----------------------------
        $display("\n--- Scenario 4: Strong input causing immediate spike ---\n");
        $display("\nTime\tIn\t  V\tSpike");
        force dut.potential = 5; // Manually preload potential
        in = 1;
        @(posedge clk);
        $display("%g\t%b\t%d\t%b", $time, in, potential, spike);
        release dut.potential;
        $display("\n");
        $finish;
    end
endmodule

