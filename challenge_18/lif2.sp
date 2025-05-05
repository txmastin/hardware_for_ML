*------------------------------------------------------------
* Leaky Integrate-and-Fire Neuron with spike_out indicator
*------------------------------------------------------------

.param Rm=1Meg
.param Cm=100p
.param Vthresh=2.2
.param Vreset=0
.param Vinput=5
.param Rstim=1Meg
.param Tstop=10m

* Input current: Vin / Rstim = 10 uA
Vin in 0 DC {Vinput}
Rstim in vmem {Rstim}

* Membrane integration path
Rleak vmem 0 {Rm}
Cmem vmem 0 {Cm} IC=0.1

* Soft reset path
* Pulse fires every 2ms for 100us (fake spike generator for now)
Vpulse reset_pulse 0 PULSE(0 1 1m 1n 1n 100u 2m)
Sreset vmem 0 reset_pulse 0 swmod

.model swmod SW(Vt=0.5 Vh=0 Ron=1k Roff=1G)

* Threshold reference
Vth vth_node 0 DC {Vthresh}

* Digital spike output: high when vmem > Vthresh
Bspike spike_out 0 V = 'V(vmem) > V(vth_node) ? 1 : 0'



* The output goes to ~100V when vmem > Vthresh

.options INTERP
.tran 1u {Tstop}
.print tran v(vmem) v(spike_out)

.control
  run
  plot v(vmem) v(spike_out)
.endc

.end

