*------------------------------------------------------------
* Self-spiking LIF neuron with stable switching
*------------------------------------------------------------

.param Rm=1Meg
.param Cm=100p
.param Vthresh=2.2
.param Vreset=0
.param Vinput=5
.param Rstim=1Meg
.param Tstop=10m

* Input current
Vin in 0 DC {Vinput}
Rstim in vmem {Rstim}

* Membrane
Rleak vmem 0 {Rm}
Cmem vmem 0 {Cm} IC=0

* Threshold
Vth vth_node 0 DC {Vthresh}

* Spike detection
Bspike spike_out 0 V = 'V(vmem) > V(vth_node) ? 1 : 0'

* Soft reset with series resistance
Sreset s_ctrl reset_node spike_out 0 swmod
Rreset vmem s_ctrl 1k
Vreset reset_node 0 DC {Vreset}

.model swmod SW(Vt=0.5 Vh=0 Ron=100 Roff=1G)

* Solver help
.options INTERP RELTOL=1e-3 ABSTOL=1n VNTOL=1u GMIN=1e-12
.ic v(vmem)=0
.tran 1u {Tstop}
.print tran v(vmem) v(spike_out)

.control
run
plot v(vmem) v(spike_out)
.endc

.end

