*------------------------------------------------------------
* LIF Neuron Benchmark (Ngspice-Compatible Final Version)
*------------------------------------------------------------

*-------- Parameters --------
.param Vth=0.5         ; Spike threshold voltage
.param Rm=1Meg         ; Leak resistance
.param Cm=100p         ; Membrane capacitance
.param Vinput=10       ; Input voltage for current source
.param Rstim=1Meg      ; Series resistance for I = 10uA
.param Tstop=10m       ; Total simulation time

*-------- Input Current Source via Voltage Divider --------
Vin in 0 DC {Vinput}
Rstim in vmem {Rstim}

*-------- Membrane RC (Leaky Integrate-and-Fire Model) --------
Rleak vmem 0 {Rm}
Cmem vmem 0 {Cm} IC=0

*-------- Threshold Reference (not active yet) --------
Vthresh vth 0 DC {Vth}

*-------- Simulation Control --------
.options INTERP
.tran 1u {Tstop}
.print tran v(vmem)

*-------- Benchmark Measurements --------
.measure TRAN spike_time CROSS v(vmem) VAL=0.5 RISE=1
.measure TRAN avg_i AVG i(Vin)
.measure TRAN avg_vmem AVG v(vmem)
.measure TRAN energy PARAM='avg_i * avg_vmem * Tstop'

*-------- Automation --------
.control
  run
  print spike_time
  print avg_i
  print avg_vmem
  print energy
.endc

.end

