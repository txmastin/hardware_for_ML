module fractional_lif #(
  parameter int N        = 3,             // number of ladder stages
  parameter int W        = 32,            // data width
  parameter int F        = 16,            // fractional bits
  // fixed-point constants (Q16.16) computed offline:
  parameter logic signed [W-1:0] K_tau0 = 32'sd655,   // Δt/C0
  parameter logic signed [W-1:0] K_leak = -32'sd13107, // -Δt/(Rleak*C0)
  parameter logic signed [W-1:0] K_Iin  = 32'sd1311,  // Δt/C0 * Iin_amp
  parameter logic signed [W-1:0] K_Ires = 32'sd3277,  // Ireset*Rleak in Q16.16
  // ladder constants: Δt/(Rj*Ci), 1/Rj, etc.
  parameter logic signed [W-1:0] A_0 = 32'sd16384, //  Δt/(R1*C1)
  parameter logic signed [W-1:0] B_0 = -32'sd16384,// -Δt*(1/R1+1/R1)/C1
  // … repeat for stages 1..N-1
)(
  input  logic                clk,
  input  logic                rst_n,
  output logic signed [W-1:0] vmem,
  output logic                spike_out
);

  // ladder node registers
  logic signed [W-1:0] vlad [0:N-1];

  // next-cycle signals
  logic signed [W-1:0] vmem_next;
  logic signed [W-1:0] vlad_next [0:N-1];
  logic                spike_next;

  // combinational compute
  always_comb begin
    // compute the ladder currents into mem:
    logic signed [W-1:0] Icap, Ir;
    Icap = 0; Ir = 0;
    for (int j = 0; j < N; j++) begin
      logic signed [W-1:0] prev = (j==0) ? vmem : vlad[j-1];
      // (prev - vlad[j]) / Rj  approximated by shift for 1/Rj
      logic signed [W-1:0] Ij = (prev - vlad[j]) >>> 4;  // example: /16
      Icap += Ij;
      Ir   += vlad[j] >>> 4;
    end

    // membrane update: vmem + K_tau0*(Iin + K_leak*vmem - Icap + Ir)
    vmem_next = vmem + K_tau0 * (K_Iin + K_leak * vmem - Icap + Ir) >>> F;

    // ladder node updates: stage j
    for (int j = 0; j < N; j++) begin
      logic signed [W-1:0] prev = (j==0) ? vmem : vlad[j-1];
      // vlad[j] + Δt/Cj * ( (prev-vlad[j])/Rj - vlad[j]/Rj )
      vlad_next[j] = vlad[j]
        + ( A_0 * (prev - vlad[j]) + B_0 * vlad[j] ) >>> F;
    end

    // spike logic
    if (vmem >= $signed(32'sd32768)) begin  // 0.5 in Q16.16 is 32768
      spike_next = 1;
      vmem_next   = vmem_next - K_Ires;
    end
    else spike_next = 0;
  end

  // sequential update
  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      vmem       <= 0;
      spike_out  <= 0;
      for (int j = 0; j < N; j++) vlad[j] <= 0;
    end else begin
      vmem      <= vmem_next;
      spike_out <= spike_next;
      for (int j = 0; j < N; j++) vlad[j] <= vlad_next[j];
    end
  end

endmodule

