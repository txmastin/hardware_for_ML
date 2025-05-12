*------------------------------------------------------------
* Stable, self-spiking LIF neuron using behavioral reset
*------------------------------------------------------------

.param Rm=1Meg
.param Cm=100p
.param Vthresh=1.8
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

* Threshold reference
Vth vth_node 0 DC {Vthresh}

* Spike output (comparator)
Bspike spike_out 0 V = '1 / (1 + exp(-(V(vmem) - V(vth_node)) / 0.01))'

* Behavioral reset: resistive pull to reset_node when spiking
Greset vmem reset_node VALUE = { (V(vmem) - V(reset_node)) * (1 / (1 + exp(-(V(vmem) - V(vth_node)) / 0.01))) * 1e-3 }


Vreset reset_node 0 DC {Vreset}

* Simulation options
.options INTERP RELTOL=1e-3 ABSTOL=1n VNTOL=1u GMIN=1e-12
.ic v(vmem)=0
.tran 1u {Tstop}
.print tran v(vmem) v(spike_out)

.control
  run
  plot v(vmem) v(spike_out)
.endc

.end

