*------------------------------------------------------------
* LIF Neuron Benchmark (Switch-Free Spiking Model)
*------------------------------------------------------------

.param Rm=1Meg
.param Cm=100p
.param Vthresh=0.5
.param Vreset=1
.param Vinput=10
.param Rstim=1Meg
.param Tstop=10m

* Input current via Vin / Rstim
Vin in 0 DC {Vinput}
Rstim in vmem {Rstim}

* Membrane RC
Rleak vmem 0 {Rm}
Cmem vmem 0 {Cm} IC=0

* Reset pulse generator — periodic pulse
* This fakes "spiking" at fixed intervals (e.g., every 1 ms)
* Use this to confirm LIF behavior without nonlinear switch
Vpulse reset_pulse 0 PULSE(0 1 1m 1n 1n 1u 2m)

* Reset transistor: controlled by pulse
Ereset_ctrl reset_node 0 VALUE = { V(reset_pulse)*{Vreset} }

* Discharge path through low resistance when reset is active
Rreset vmem reset_node 1k

.options INTERP
.tran 1u {Tstop}
.print tran v(vmem)

.control
  run
  plot v(vmem)
.endc

.end

